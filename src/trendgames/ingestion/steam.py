from __future__ import annotations

from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric, simulated_signal


def collect_steam_metrics(games: Sequence[GameSeed], collected_at: datetime) -> list[CollectedMetric]:
    metrics: list[CollectedMetric] = []
    for game in games:
        steam_factor = 1.0 if game.steam_appid is not None else 0.78
        players = round(
            simulated_signal(
                game.game_id,
                "steam",
                collected_at,
                base_low=220.0,
                base_high=85_000.0,
            )
            * steam_factor,
            2,
        )
        metrics.append(
            CollectedMetric(
                game_id=game.game_id,
                game_name=game.name,
                platform="steam",
                metric_type="players_current",
                value=players,
                unit="players",
                raw={"simulated": True, "steam_appid": game.steam_appid},
            )
        )
    return metrics
