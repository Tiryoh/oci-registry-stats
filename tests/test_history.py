from datetime import datetime, timezone

from registry_stats.history import historical_diff
from registry_stats.models import Snapshot


NOW = datetime(2026, 6, 15, 0, 15, tzinfo=timezone.utc)


def _snapshot(total: int, days_ago: int = 0, version_id: str | None = None) -> Snapshot:
    identity = {}
    if version_id:
        identity["version_id"] = version_id
    return Snapshot(
        target_id="target",
        registry="ghcr" if version_id else "dockerhub",
        scope="tag" if version_id else "repository",
        collected_at=NOW if days_ago == 0 else NOW.replace(day=NOW.day - days_ago),
        status="ok",
        identity=identity,
        metrics={"total_downloads": total},
    )


def test_historical_diff_returns_difference() -> None:
    value, warning = historical_diff(_snapshot(1300), [_snapshot(1000, 7)], 7, 36)

    assert value == 300
    assert warning is None


def test_historical_diff_returns_none_without_baseline() -> None:
    value, warning = historical_diff(_snapshot(1300), [], 30, 36)

    assert value is None
    assert warning is None


def test_historical_diff_handles_counter_decrease() -> None:
    value, warning = historical_diff(_snapshot(900), [_snapshot(1000, 7)], 7, 36)

    assert value is None
    assert warning == "counter_decreased"


def test_historical_diff_does_not_cross_ghcr_version_id() -> None:
    value, warning = historical_diff(
        _snapshot(1300, version_id="new"),
        [_snapshot(1000, 7, version_id="old")],
        7,
        36,
    )

    assert value is None
    assert warning is None
