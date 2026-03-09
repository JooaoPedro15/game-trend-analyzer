from __future__ import annotations

from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric, simulated_signal


def collect_youtube_metrics(games: Sequence[GameSeed], collected_at: datetime) -> list[CollectedMetric]:
    metrics: list[CollectedMetric] = []
    for game in games:
        views = round(
            simulated_signal(
                game.game_id,
                "youtube",
                collected_at,
                base_low=8_000.0,
                base_high=650_000.0,
            ),
            2,
        )
        uploads = float(
            max(
                2,
                int(
                    simulated_signal(
                        game.game_id,
                        "youtube-uploads",
                        collected_at,
                        base_low=4.0,
                        base_high=200.0,
                        volatility=0.18,
                    )
                ),
            )
        )

        metrics.append(
            CollectedMetric(
                game_id=game.game_id,
                game_name=game.name,
                platform="youtube",
                metric_type="attention_views",
                value=views,
                unit="views",
                raw={"simulated": True},
            )
        )
        metrics.append(
            CollectedMetric(
                game_id=game.game_id,
                game_name=game.name,
                platform="youtube",
                metric_type="creation_uploads",
                value=uploads,
                unit="uploads",
                raw={"simulated": True},
            )
        )
    return metrics
