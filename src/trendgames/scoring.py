from __future__ import annotations

from collections import defaultdict
import math
from statistics import mean

from trendgames.domain import ChannelProfile, TrendScore

PLATFORM_PRIMARY_METRICS: dict[str, tuple[str, ...]] = {
    "twitch": ("attention_viewers", "supply_streams"),
    "youtube": ("attention_views", "creation_uploads"),
    "steam": ("players_current",),
    "tiktok": ("attention_views", "hashtag_rank"),
    "instagram": ("attention_views", "creation_uploads"),
    "reference_channels": ("coverage_count",),
    "reference_channels_youtube": ("coverage_count",),
    "reference_channels_tiktok": ("coverage_count",),
}

KNOWN_PLATFORMS = (
    "twitch", "youtube", "steam", "tiktok", "instagram",
    "reference_channels", "reference_channels_youtube", "reference_channels_tiktok",
)


def calculate_scores(
    snapshot_id: int,
    current_metrics: list[dict[str, object]],
    previous_metrics: list[dict[str, object]],
    profile: ChannelProfile,
) -> list[TrendScore]:
    current = _select_primary_platform_values(current_metrics)
    previous = _select_primary_platform_values(previous_metrics)

    if not current:
        return []

    pop_percentiles = _percentiles_per_platform(current)
    growth_percentiles, growth_raw = _growth_percentiles(current, previous)

    fit_enabled = bool(profile.preferred_game_types or profile.avoided_game_types)
    fit_weight = 0.10 if fit_enabled else 0.0

    weights = {
        "popularity": 0.40,
        "growth": 0.30,
        "multiplatform": 0.20,
        "fit": fit_weight,
    }
    weight_sum = sum(weights.values()) or 1.0

    preferred_tags = {item.casefold() for item in profile.preferred_game_types}
    avoided_tags = {item.casefold() for item in profile.avoided_game_types}

    scores: list[TrendScore] = []
    for game_id, game_data in current.items():
        platform_values: dict[str, float] = game_data["platform_values"]  # type: ignore[assignment]
        tags: list[str] = game_data["tags"]  # type: ignore[assignment]

        per_platform_pop: dict[str, float] = {}
        per_platform_growth: dict[str, float] = {}
        growth_delta_log: dict[str, float] = {}
        strong_platforms: list[str] = []
        for platform in platform_values:
            pop_pct = pop_percentiles.get(platform, {}).get(game_id, 0.5)
            growth_pct = growth_percentiles.get(platform, {}).get(game_id, 0.5)
            per_platform_pop[platform] = pop_pct
            per_platform_growth[platform] = growth_pct
            growth_delta_log[platform] = round(growth_raw.get(platform, {}).get(game_id, 0.0), 6)
            if pop_pct >= 0.70:
                strong_platforms.append(platform)

        popularity_score = _mean_score(per_platform_pop.values())
        growth_score = _mean_score(per_platform_growth.values())
        multiplatform_score = min(100.0, float(len(strong_platforms)) * 35.0)

        fit_score, fit_details = _fit_score(tags, preferred_tags, avoided_tags)

        total = (
            weights["popularity"] * popularity_score
            + weights["growth"] * growth_score
            + weights["multiplatform"] * multiplatform_score
            + weights["fit"] * fit_score
        ) / weight_sum

        explanation = {
            "trend_label": _trend_label(total),
            "strong_platforms": strong_platforms,
            "platform_percentiles": {k: round(v * 100, 2) for k, v in per_platform_pop.items()},
            "growth_percentiles": {k: round(v * 100, 2) for k, v in per_platform_growth.items()},
            "growth_delta_log": growth_delta_log,
            "fit": fit_details,
            "missing_platforms": sorted(set(KNOWN_PLATFORMS) - set(platform_values)),
        }

        scores.append(
            TrendScore(
                snapshot_id=snapshot_id,
                game_id=game_id,
                game_name=str(game_data["game_name"]),
                score_total=round(total, 2),
                score_popularity=round(popularity_score, 2),
                score_growth=round(growth_score, 2),
                score_multiplatform=round(multiplatform_score, 2),
                score_fit=round(fit_score, 2),
                explanation=explanation,
            )
        )

    return sorted(scores, key=lambda item: item.score_total, reverse=True)


def _select_primary_platform_values(metrics: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}

    for row in metrics:
        game_id = str(row["game_id"])
        platform = str(row["platform"])
        metric_type = str(row["metric_type"])
        value = float(row["value"])

        entry = grouped.setdefault(
            game_id,
            {
                "game_name": str(row["game_name"]),
                "tags": [str(tag).strip() for tag in row.get("tags", []) if str(tag).strip()],
                "raw_platform_metrics": defaultdict(dict),
            },
        )
        raw_metrics: defaultdict[str, dict[str, float]] = entry["raw_platform_metrics"]  # type: ignore[assignment]
        raw_metrics[platform][metric_type] = value

    for entry in grouped.values():
        raw_metrics: defaultdict[str, dict[str, float]] = entry.pop("raw_platform_metrics")  # type: ignore[assignment]
        platform_values: dict[str, float] = {}
        for platform, metric_map in raw_metrics.items():
            priority = PLATFORM_PRIMARY_METRICS.get(platform, ())
            selected = None
            for metric_type in priority:
                if metric_type in metric_map:
                    selected = metric_map[metric_type]
                    break
            if selected is None:
                selected = max(metric_map.values())
            platform_values[platform] = float(selected)
        entry["platform_values"] = platform_values
    return grouped


def _percentiles_per_platform(
    grouped: dict[str, dict[str, object]]
) -> dict[str, dict[str, float]]:
    values_by_platform: dict[str, dict[str, float]] = defaultdict(dict)
    for game_id, game_data in grouped.items():
        platform_values: dict[str, float] = game_data["platform_values"]  # type: ignore[assignment]
        for platform, value in platform_values.items():
            values_by_platform[platform][game_id] = value

    result: dict[str, dict[str, float]] = {}
    for platform, values_by_game in values_by_platform.items():
        result[platform] = _percentile_rank(values_by_game)
    return result


def _growth_percentiles(
    current: dict[str, dict[str, object]],
    previous: dict[str, dict[str, object]],
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    if not previous:
        neutral_percentiles = _neutral_percentiles(current)
        return neutral_percentiles, {platform: {} for platform in neutral_percentiles}

    growth_values_by_platform: dict[str, dict[str, float]] = defaultdict(dict)
    for game_id, current_data in current.items():
        current_platform_values: dict[str, float] = current_data["platform_values"]  # type: ignore[assignment]
        previous_platform_values: dict[str, float] = {}
        if game_id in previous:
            previous_platform_values = previous[game_id]["platform_values"]  # type: ignore[assignment]

        for platform, current_value in current_platform_values.items():
            previous_value = previous_platform_values.get(platform)
            if previous_value is None:
                growth_raw = 0.0
            else:
                growth_raw = math.log1p(current_value) - math.log1p(previous_value)
            growth_values_by_platform[platform][game_id] = growth_raw

    growth_percentiles: dict[str, dict[str, float]] = {}
    for platform, values in growth_values_by_platform.items():
        growth_percentiles[platform] = _percentile_rank(values)
    return growth_percentiles, growth_values_by_platform


def _neutral_percentiles(current: dict[str, dict[str, object]]) -> dict[str, dict[str, float]]:
    neutral: dict[str, dict[str, float]] = defaultdict(dict)
    for game_id, current_data in current.items():
        platform_values: dict[str, float] = current_data["platform_values"]  # type: ignore[assignment]
        for platform in platform_values:
            neutral[platform][game_id] = 0.5
    return dict(neutral)


def _percentile_rank(values_by_game: dict[str, float]) -> dict[str, float]:
    if not values_by_game:
        return {}
    if len(values_by_game) == 1:
        return {next(iter(values_by_game)): 1.0}

    sorted_items = sorted(values_by_game.items(), key=lambda item: item[1])
    denominator = len(sorted_items) - 1
    result: dict[str, float] = {}
    i = 0
    while i < len(sorted_items):
        j = i + 1
        val = sorted_items[i][1]
        while j < len(sorted_items) and sorted_items[j][1] == val:
            j += 1
        avg_pct = (i + j - 1) / 2 / denominator
        for k in range(i, j):
            result[sorted_items[k][0]] = avg_pct
        i = j
    return result


def _mean_score(values: object) -> float:
    numeric = [float(value) for value in values]
    if not numeric:
        return 0.0
    return mean(numeric) * 100.0


def _fit_score(tags: list[str], preferred_tags: set[str], avoided_tags: set[str]) -> tuple[float, dict[str, object]]:
    tag_set = {tag.casefold() for tag in tags}
    preferred_hits = sorted(tag_set.intersection(preferred_tags))
    avoided_hits = sorted(tag_set.intersection(avoided_tags))

    score = 50.0
    score += min(30.0, len(preferred_hits) * 12.0)
    score -= min(40.0, len(avoided_hits) * 18.0)
    score = max(0.0, min(100.0, score))

    details = {
        "preferred_matches": preferred_hits,
        "avoided_matches": avoided_hits,
        "tags_used": sorted(tag_set),
    }
    return score, details


def _trend_label(score_total: float) -> str:
    if score_total >= 85:
        return "muito_em_alta"
    if score_total >= 70:
        return "em_alta"
    if score_total >= 50:
        return "monitorar"
    return "baixo_sinal"
