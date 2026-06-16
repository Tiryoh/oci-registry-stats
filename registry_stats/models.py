from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Registry = Literal["dockerhub", "ghcr"]
Scope = Literal["repository", "package", "tag"]
Status = Literal["ok", "error"]
Precision = Literal["exact", "rounded", "unknown"]


class OutputConfig(BaseModel):
    dir: str = "data"
    latest_json: str = "latest.json"
    latest_csv: str = "latest.csv"
    snapshots_dir: str = "snapshots"
    shields_dir: str = "shields"


class CollectionConfig(BaseModel):
    user_agent: str = "registry-stats/0.1"
    timeout_seconds: float = 20
    retry_count: int = 3
    retry_backoff_seconds: float = 2
    history_window_tolerance_hours: int = 36


class TargetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    registry: Registry
    scope: Scope
    namespace: str | None = None
    repository: str | None = None
    owner_type: Literal["user", "org"] | None = None
    owner: str | None = None
    package: str | None = None
    tag: str | None = None
    repository_owner: str | None = None
    repository_name: str | None = None


class AppConfig(BaseModel):
    schema_version: int = 1
    output: OutputConfig = Field(default_factory=OutputConfig)
    collection: CollectionConfig = Field(default_factory=CollectionConfig)
    targets: list[TargetConfig]


class Metrics(BaseModel):
    total_downloads: int | None = None
    weekly_downloads: int | None = None
    monthly_downloads: int | None = None
    today_downloads: int | None = None


class Snapshot(BaseModel):
    schema_version: int = 1
    target_id: str
    registry: Registry
    scope: Scope
    collected_at: datetime
    status: Status
    identity: dict[str, str | int | bool | None] = Field(default_factory=dict)
    metrics: Metrics = Field(default_factory=Metrics)
    methods: dict[str, str] = Field(default_factory=dict)
    precision: dict[str, Precision] = Field(default_factory=dict)
    source: dict[str, str] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CollectResult(BaseModel):
    snapshot: Snapshot
    direct_weekly: bool = False
    direct_monthly: bool = False
