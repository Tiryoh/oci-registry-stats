from pathlib import Path

from registry_stats.parsing.ghcr_html import (
    parse_ghcr_package_downloads,
    parse_ghcr_version_downloads,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_ghcr_version_downloads() -> None:
    metrics = parse_ghcr_version_downloads((FIXTURES / "ghcr_version.html").read_text())

    assert metrics == {
        "total_downloads": 25,
        "monthly_downloads": 25,
        "weekly_downloads": 16,
        "today_downloads": 0,
    }


def test_parse_ghcr_package_downloads_prefers_title() -> None:
    parsed = parse_ghcr_package_downloads((FIXTURES / "ghcr_package.html").read_text())

    assert parsed.total_downloads == 10342
    assert parsed.precision == "exact"
