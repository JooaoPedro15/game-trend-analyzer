from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GameSeed:
    game_id: str
    name: str
    tags: list[str] = field(default_factory=list)
    steam_appid: int | None = None
    youtube_queries: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ChannelProfile:
    channel_name: str = "Canal"
    content_type: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    preferred_game_types: list[str] = field(default_factory=list)
    avoided_game_types: list[str] = field(default_factory=list)
    video_length_min: int | None = None
    video_length_max: int | None = None
    reference_channels_youtube: list[str] = field(default_factory=list)
    reference_channels_tiktok: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlatformMetric:
    snapshot_id: int
    game_id: str
    game_name: str
    platform: str
    metric_type: str
    value: float
    unit: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrendScore:
    snapshot_id: int
    game_id: str
    game_name: str
    score_total: float
    score_popularity: float
    score_growth: float
    score_multiplatform: float
    score_fit: float
    explanation: dict[str, Any]
