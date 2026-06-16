from __future__ import annotations

import os
from datetime import datetime

from registry_stats.clients.http import HttpClient
from registry_stats.models import CollectResult, Snapshot, TargetConfig


AUTH_URL = "https://hub.docker.com/v2/auth/token"


def collect_dockerhub_repository(
    target: TargetConfig, client: HttpClient, collected_at: datetime
) -> CollectResult:
    if not target.namespace or not target.repository:
        raise ValueError(f"{target.id}: dockerhub repository target requires namespace and repository")

    url = f"https://hub.docker.com/v2/namespaces/{target.namespace}/repositories/{target.repository}"
    headers = _auth_headers(client)
    data = client.get_json(url, headers=headers)
    pull_count = data.get("pull_count")
    if pull_count is None:
        raise ValueError(f"{target.id}: pull_count not found in Docker Hub response")

    snapshot = Snapshot(
        target_id=target.id,
        registry="dockerhub",
        scope="repository",
        collected_at=collected_at,
        status="ok",
        identity={"namespace": target.namespace, "repository": target.repository},
        metrics={"total_downloads": int(pull_count)},
        methods={
            "total_downloads": "dockerhub_repository_api",
            "weekly_downloads": "historical_diff",
            "monthly_downloads": "historical_diff",
        },
        precision={
            "total_downloads": "exact",
            "weekly_downloads": "unknown",
            "monthly_downloads": "unknown",
        },
        source={"url": url},
    )
    return CollectResult(snapshot=snapshot)


def _auth_headers(client: HttpClient) -> dict[str, str] | None:
    username = os.getenv("DOCKERHUB_USERNAME")
    pat = os.getenv("DOCKERHUB_PAT")
    if not username or not pat:
        return None
    token = client.post_json(AUTH_URL, {"identifier": username, "secret": pat}).get("access_token")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}
