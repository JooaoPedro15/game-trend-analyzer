from __future__ import annotations

from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric, simulated_signal


def collect_twitch_metrics(games: Sequence[GameSeed], collected_at: datetime) -> list[CollectedMetric]:
    metrics: list[CollectedMetric] = []
    for game in games:
        viewers = round(
            simulated_signal(
                game.game_id,
                "twitch",
                collected_at,
                base_low=350.0,
                base_high=18_000.0,
            ),
            2,
        )
        streams = float(max(4, int(viewers / 220)))

        metrics.append(
            CollectedMetric(
                game_id=game.game_id,
                game_name=game.name,
                platform="twitch",
                metric_type="attention_viewers",
                value=viewers,
                unit="viewers",
                raw={"simulated": True},
            )
        )
        metrics.append(
            CollectedMetric(
                game_id=game.game_id,
                game_name=game.name,
                platform="twitch",
                metric_type="supply_streams",
                value=streams,
                unit="streams",
                raw={"simulated": True},
            )
        )
    return metrics
