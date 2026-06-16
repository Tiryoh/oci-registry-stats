from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

from registry_stats.parsing.numbers import parse_compact_int


_VALUE = r"([0-9][0-9,]*(?:\.[0-9]+)?[KMB]?)"
PATTERNS = {
    "total_downloads": re.compile(rf"Total downloads\s+{_VALUE}", re.IGNORECASE),
    "monthly_downloads": re.compile(rf"Last 30 days\s+{_VALUE}", re.IGNORECASE),
    "weekly_downloads": re.compile(rf"Last week\s+{_VALUE}", re.IGNORECASE),
    "today_downloads": re.compile(rf"Today\s+{_VALUE}", re.IGNORECASE),
}


@dataclass(frozen=True)
class PackageDownloads:
    total_downloads: int
    precision: str


def _visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style"]):
        node.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))


def parse_ghcr_version_downloads(html: str) -> dict[str, int]:
    text = _visible_text(html)
    metrics: dict[str, int] = {}
    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            metrics[key] = parse_compact_int(match.group(1))
    return metrics


def parse_ghcr_package_downloads(html: str) -> PackageDownloads:
    soup = BeautifulSoup(html, "html.parser")
    total_label = soup.find(string=re.compile(r"Total downloads", re.IGNORECASE))
    if total_label:
        parent = total_label.parent
        search_root = parent.parent if parent and parent.parent else soup
        titled = search_root.find(attrs={"title": re.compile(r"^[0-9][0-9,]*$")})
        if titled and titled.get("title"):
            return PackageDownloads(int(titled["title"].replace(",", "")), "exact")

    text = _visible_text(html)
    match = PATTERNS["total_downloads"].search(text)
    if match:
        raw = match.group(1)
        precision = "rounded" if re.search(r"[KMB]", raw, re.IGNORECASE) else "exact"
        return PackageDownloads(parse_compact_int(raw), precision)

    raise ValueError("Total downloads not found in GHCR package page")
