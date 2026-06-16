from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import traceback

from registry_stats.clients.http import HttpClient
from registry_stats.collectors.dockerhub import collect_dockerhub_repository
from registry_stats.collectors.ghcr import collect_ghcr
from registry_stats.config import load_config
from registry_stats.history import append_snapshot, historical_diff, read_snapshots, snapshot_path
from registry_stats.models import AppConfig, CollectResult, Snapshot, TargetConfig
from registry_stats.render import write_outputs


def collect_from_config(config_path: str | Path) -> int:
    config = load_config(config_path)
    return collect(config)


def collect(config: AppConfig) -> int:
    snapshots_dir = Path(config.output.dir) / config.output.snapshots_dir
    collected_at = datetime.now(timezone.utc)
    client = HttpClient(config.collection)
    results: list[Snapshot] = []
    ok_count = 0
    try:
        for target in config.targets:
            result = _collect_target(target, config, client, snapshots_dir, collected_at)
            append_snapshot(snapshot_path(snapshots_dir, target.id), result)
            results.append(result)
            if result.status == "ok":
                ok_count += 1
    finally:
        client.close()

    write_outputs(config, results)
    return 0 if ok_count > 0 else 1


def _collect_target(
    target: TargetConfig,
    config: AppConfig,
    client: HttpClient,
    snapshots_dir: Path,
    collected_at: datetime,
) -> Snapshot:
    try:
        result = _run_collector(target, client, collected_at)
        previous = read_snapshots(snapshot_path(snapshots_dir, target.id))
        _fill_historical_metrics(result, previous, config.collection.history_window_tolerance_hours)
        return result.snapshot
    except Exception as exc:
        return Snapshot(
            target_id=target.id,
            registry=target.registry,
            scope=target.scope,
            collected_at=collected_at,
            status="error",
            identity=_target_identity(target),
            errors=[f"{type(exc).__name__}: {exc}"],
            warnings=[traceback.format_exc(limit=1).strip()],
        )


def _run_collector(target: TargetConfig, client: HttpClient, collected_at: datetime) -> CollectResult:
    if target.registry == "dockerhub" and target.scope == "repository":
        return collect_dockerhub_repository(target, client, collected_at)
    if target.registry == "ghcr":
        return collect_ghcr(target, client, collected_at)
    raise ValueError(f"{target.id}: unsupported target {target.registry}/{target.scope}")


def _fill_historical_metrics(
    result: CollectResult, previous: list[Snapshot], tolerance_hours: int
) -> None:
    snapshot = result.snapshot
    if not result.direct_weekly and snapshot.metrics.weekly_downloads is None:
        value, warning = historical_diff(snapshot, previous, 7, tolerance_hours)
        snapshot.metrics.weekly_downloads = value
        if value is not None:
            snapshot.precision["weekly_downloads"] = "exact"
        if warning:
            snapshot.warnings.append(warning)
    if not result.direct_monthly and snapshot.metrics.monthly_downloads is None:
        value, warning = historical_diff(snapshot, previous, 30, tolerance_hours)
        snapshot.metrics.monthly_downloads = value
        if value is not None:
            snapshot.precision["monthly_downloads"] = "exact"
        if warning:
            snapshot.warnings.append(warning)


def _target_identity(target: TargetConfig) -> dict[str, str | None]:
    return {
        key: value
        for key, value in {
            "namespace": target.namespace,
            "repository": target.repository,
            "owner": target.owner,
            "package": target.package,
            "tag": target.tag,
        }.items()
        if value is not None
    }
