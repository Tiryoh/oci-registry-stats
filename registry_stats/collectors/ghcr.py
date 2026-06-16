from __future__ import annotations

import os
from datetime import datetime
from urllib.parse import quote

from registry_stats.clients.http import HttpClient
from registry_stats.models import CollectResult, Snapshot, TargetConfig
from registry_stats.parsing.ghcr_html import (
    parse_ghcr_package_downloads,
    parse_ghcr_version_downloads,
)


def collect_ghcr(target: TargetConfig, client: HttpClient, collected_at: datetime) -> CollectResult:
    if target.scope == "package":
        return _collect_package(target, client, collected_at)
    if target.scope == "tag":
        return _collect_tag(target, client, collected_at)
    raise ValueError(f"{target.id}: unsupported GHCR scope {target.scope}")


def _collect_package(target: TargetConfig, client: HttpClient, collected_at: datetime) -> CollectResult:
    _require(target, "owner", "package", "repository_owner", "repository_name")
    url = (
        f"https://github.com/{target.repository_owner}/{target.repository_name}"
        f"/pkgs/container/{quote(target.package or '', safe='')}"
    )
    parsed = parse_ghcr_package_downloads(client.get_text(url))
    snapshot = Snapshot(
        target_id=target.id,
        registry="ghcr",
        scope="package",
        collected_at=collected_at,
        status="ok",
        identity={"owner": target.owner, "package": target.package},
        metrics={"total_downloads": parsed.total_downloads},
        methods={
            "total_downloads": "ghcr_package_page_scrape",
            "weekly_downloads": "historical_diff",
            "monthly_downloads": "historical_diff",
        },
        precision={
            "total_downloads": parsed.precision,
            "weekly_downloads": "unknown",
            "monthly_downloads": "unknown",
        },
        source={"url": url},
    )
    return CollectResult(snapshot=snapshot)


def _collect_tag(target: TargetConfig, client: HttpClient, collected_at: datetime) -> CollectResult:
    _require(target, "owner_type", "owner", "package", "tag", "repository_owner", "repository_name")
    version = _find_version_for_tag(target, client)
    version_id = str(version["id"])
    digest = _version_digest(version)
    url = (
        f"https://github.com/{target.repository_owner}/{target.repository_name}"
        f"/pkgs/container/{quote(target.package or '', safe='')}/{version_id}"
        f"?tag={quote(target.tag or '', safe='')}"
    )
    metrics = parse_ghcr_version_downloads(client.get_text(url))
    if "total_downloads" not in metrics:
        raise ValueError(f"{target.id}: Total downloads not found in GHCR version page")

    snapshot = Snapshot(
        target_id=target.id,
        registry="ghcr",
        scope="tag",
        collected_at=collected_at,
        status="ok",
        identity={
            "owner": target.owner,
            "package": target.package,
            "tag": target.tag,
            "version_id": version_id,
            "digest": digest,
        },
        metrics=metrics,
        methods={
            "total_downloads": "ghcr_version_page_scrape",
            "weekly_downloads": "ghcr_version_page_scrape"
            if "weekly_downloads" in metrics
            else "historical_diff",
            "monthly_downloads": "ghcr_version_page_scrape"
            if "monthly_downloads" in metrics
            else "historical_diff",
            "today_downloads": "ghcr_version_page_scrape",
        },
        precision={
            "total_downloads": "exact",
            "weekly_downloads": "exact" if "weekly_downloads" in metrics else "unknown",
            "monthly_downloads": "exact" if "monthly_downloads" in metrics else "unknown",
        },
        source={"url": url},
    )
    return CollectResult(
        snapshot=snapshot,
        direct_weekly="weekly_downloads" in metrics,
        direct_monthly="monthly_downloads" in metrics,
    )


def _find_version_for_tag(target: TargetConfig, client: HttpClient) -> dict:
    package = quote(target.package or "", safe="")
    if target.owner_type == "org":
        url = f"https://api.github.com/orgs/{target.owner}/packages/container/{package}/versions"
    else:
        url = f"https://api.github.com/users/{target.owner}/packages/container/{package}/versions"

    headers = _github_headers()
    page = 1
    while True:
        versions = client.get_json(f"{url}?per_page=100&page={page}", headers=headers)
        if not versions:
            break
        for version in versions:
            tags = version.get("metadata", {}).get("container", {}).get("tags", [])
            if target.tag in tags:
                return version
        page += 1
    raise ValueError(f"{target.id}: GHCR version for tag {target.tag!r} not found")


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": os.getenv("GITHUB_API_VERSION", "2022-11-28"),
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _version_digest(version: dict) -> str | None:
    container = version.get("metadata", {}).get("container", {})
    digest = container.get("digest")
    if digest:
        return str(digest)
    return None


def _require(target: TargetConfig, *fields: str) -> None:
    missing = [field for field in fields if getattr(target, field) in (None, "")]
    if missing:
        raise ValueError(f"{target.id}: missing required fields: {', '.join(missing)}")
