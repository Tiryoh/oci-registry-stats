from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from registry_stats.models import Snapshot


def snapshot_path(base_dir: Path, target_id: str) -> Path:
    return base_dir / f"{target_id}.jsonl"


def read_snapshots(path: Path) -> list[Snapshot]:
    if not path.exists():
        return []
    snapshots: list[Snapshot] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                snapshots.append(Snapshot.model_validate_json(line))
    return snapshots


def append_snapshot(path: Path, snapshot: Snapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(snapshot.model_dump_json(exclude_none=True))
        f.write("\n")


def historical_diff(
    current: Snapshot, snapshots: list[Snapshot], days: int, tolerance_hours: int
) -> tuple[int | None, str | None]:
    target_time = current.collected_at - timedelta(days=days)
    candidates = [
        snapshot
        for snapshot in snapshots
        if snapshot.status == "ok"
        and snapshot.metrics.total_downloads is not None
        and _same_identity_for_diff(current, snapshot)
    ]
    if not candidates:
        return None, None

    baseline = min(
        candidates,
        key=lambda snapshot: abs((snapshot.collected_at - target_time).total_seconds()),
    )
    delta = target_time - baseline.collected_at
    if abs(delta.total_seconds()) > tolerance_hours * 3600:
        return None, None

    current_total = current.metrics.total_downloads
    baseline_total = baseline.metrics.total_downloads
    if current_total is None or baseline_total is None:
        return None, None

    diff = current_total - baseline_total
    if diff < 0:
        return None, "counter_decreased"
    return diff, None


def load_latest_snapshot(path: Path) -> dict | None:
    snapshots = read_snapshots(path)
    if not snapshots:
        return None
    return json.loads(snapshots[-1].model_dump_json(exclude_none=True))


def _same_identity_for_diff(current: Snapshot, baseline: Snapshot) -> bool:
    if current.registry == "ghcr" and current.scope == "tag":
        return current.identity.get("version_id") == baseline.identity.get("version_id")
    return True
