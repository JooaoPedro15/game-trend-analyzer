from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import math
from typing import Any


@dataclass(frozen=True)
class CollectedMetric:
    game_id: str
    game_name: str
    platform: str
    metric_type: str
    value: float
    unit: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


def simulated_signal(
    game_id: str,
    platform: str,
    collected_at: datetime,
    *,
    base_low: float,
    base_high: float,
    volatility: float = 0.22,
) -> float:
    base_factor = _stable_fraction(f"{game_id}:{platform}:base")
    base_value = base_low + base_factor * (base_high - base_low)

    phase = _stable_fraction(f"{game_id}:{platform}:phase") * math.tau
    step = collected_at.timestamp() / (60 * 60 * 6)
    wave = math.sin(step + phase) * volatility

    jitter = (_stable_fraction(f"{game_id}:{platform}:{collected_at:%Y%m%d%H}") - 0.5) * volatility
    adjusted = base_value * (1.0 + wave + jitter)
    return max(1.0, adjusted)


def _stable_fraction(key: str) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)
