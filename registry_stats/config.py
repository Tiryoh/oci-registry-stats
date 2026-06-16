from __future__ import annotations

from pathlib import Path

import yaml

from registry_stats.models import AppConfig


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data)
