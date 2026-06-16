from __future__ import annotations

from decimal import Decimal
import re


_COMPACT_RE = re.compile(r"^\s*([0-9][0-9,]*(?:\.[0-9]+)?)([KMB])?\s*$", re.IGNORECASE)


def parse_compact_int(value: str) -> int:
    match = _COMPACT_RE.match(value)
    if not match:
        raise ValueError(f"invalid compact integer: {value!r}")

    number = Decimal(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").upper()
    multiplier = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suffix]
    return int(number * multiplier)


def format_compact(value: int | None) -> str:
    if value is None:
        return "unknown"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m".replace(".0m", "m")
    if value >= 1_000:
        return f"{value / 1_000:.1f}k".replace(".0k", "k")
    return str(value)
