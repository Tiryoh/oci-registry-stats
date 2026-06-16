from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from registry_stats.models import AppConfig, Snapshot
from registry_stats.parsing.numbers import format_compact


def write_outputs(config: AppConfig, snapshots: list[Snapshot]) -> None:
    output_dir = Path(config.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_latest_json(output_dir / config.output.latest_json, snapshots)
    write_latest_csv(output_dir / config.output.latest_csv, snapshots)
    write_shields(output_dir / config.output.shields_dir, snapshots)


def write_latest_json(path: Path, snapshots: list[Snapshot]) -> None:
    data = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets": [_latest_entry(snapshot) for snapshot in snapshots],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_latest_csv(path: Path, snapshots: list[Snapshot]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "registry",
                "scope",
                "name",
                "total_downloads",
                "weekly_downloads",
                "monthly_downloads",
                "status",
            ],
        )
        writer.writeheader()
        for snapshot in snapshots:
            writer.writerow(
                {
                    "id": snapshot.target_id,
                    "registry": snapshot.registry,
                    "scope": snapshot.scope,
                    "name": _target_name(snapshot),
                    "total_downloads": _csv_value(snapshot.metrics.total_downloads),
                    "weekly_downloads": _csv_value(snapshot.metrics.weekly_downloads),
                    "monthly_downloads": _csv_value(snapshot.metrics.monthly_downloads),
                    "status": snapshot.status,
                }
            )


def write_shields(path: Path, snapshots: list[Snapshot]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for snapshot in snapshots:
        for metric, suffix, label in [
            ("total_downloads", "total", "downloads"),
            ("weekly_downloads", "weekly", "downloads / week"),
            ("monthly_downloads", "monthly", "downloads / month"),
        ]:
            value = getattr(snapshot.metrics, metric)
            payload = {
                "schemaVersion": 1,
                "label": _badge_label(snapshot, label),
                "message": format_compact(value),
                "color": "blue" if value is not None else "lightgrey",
            }
            badge_path = path / f"{snapshot.target_id}_{suffix}.json"
            badge_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")


def _latest_entry(snapshot: Snapshot) -> dict:
    return {
        "id": snapshot.target_id,
        "registry": snapshot.registry,
        "scope": snapshot.scope,
        "name": _target_name(snapshot),
        "total_downloads": snapshot.metrics.total_downloads,
        "weekly_downloads": snapshot.metrics.weekly_downloads,
        "monthly_downloads": snapshot.metrics.monthly_downloads,
        "status": snapshot.status,
        "methods": snapshot.methods,
    }


def _target_name(snapshot: Snapshot) -> str:
    identity = snapshot.identity
    if snapshot.registry == "dockerhub":
        return f"{identity.get('namespace')}/{identity.get('repository')}"
    if snapshot.scope == "tag":
        return f"ghcr.io/{str(identity.get('owner')).lower()}/{identity.get('package')}:{identity.get('tag')}"
    return f"ghcr.io/{str(identity.get('owner')).lower()}/{identity.get('package')}"


def _badge_label(snapshot: Snapshot, label: str) -> str:
    prefix = "docker pulls" if snapshot.registry == "dockerhub" else "ghcr downloads"
    if label == "downloads":
        return prefix
    return f"{prefix} {label.removeprefix('downloads ')}"


def _csv_value(value: int | None) -> str:
    return "" if value is None else str(value)
