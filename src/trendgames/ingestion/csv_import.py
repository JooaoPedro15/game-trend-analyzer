from __future__ import annotations

import csv
from pathlib import Path
import re
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric


def import_csv_metrics(csv_path: Path, games: Sequence[GameSeed]) -> list[CollectedMetric]:
    if not csv_path.exists():
        return []

    by_name = {_normalize_name(game.name): game for game in games}
    metrics: list[CollectedMetric] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            game_name = str(row.get("game_name", "")).strip()
            platform = str(row.get("platform", "")).strip().lower()
            metric_type = str(row.get("metric_type", "")).strip().lower()
            value_raw = str(row.get("value", "")).strip()
            unit = str(row.get("unit", "")).strip()

            if not game_name or not platform or not metric_type or not value_raw:
                continue

            game = by_name.get(_normalize_name(game_name))
            if game is None:
                continue

            try:
                value = float(value_raw)
            except ValueError:
                continue

            metrics.append(
                CollectedMetric(
                    game_id=game.game_id,
                    game_name=game.name,
                    platform=platform,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    raw={"source": "csv", "csv_game_name": game_name},
                )
            )
    return metrics


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())
