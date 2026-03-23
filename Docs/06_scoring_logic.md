# Ranking logic (MVP)

## Goal
Produce a ranking of games for "record now" that is:
- explainable (decomposition by factors)
- current (considers recency)
- multiplatform (when possible)
- customizable (channel profile)

## Score components (0..100)

ScoreTrending =
  w_pop  * Popularity +
  w_grow * Growth +
  w_multi* PlatformDistribution +
  w_fit  * ChannelCompatibility

Suggested weights (MVP):
- w_pop = 0.40
- w_grow = 0.30
- w_multi = 0.20
- w_fit = 0.10 (or 0 if no profile is provided)

## 1) Overall popularity
Input: "level" metrics per platform.
Examples:
- Twitch viewers (attention_viewers)
- Aggregated YouTube views (attention_views)
- Steam players_current

How to normalize:
- For each platform, calculate the game's rank_percentile in the snapshot.
- Popularity = weighted average of available percentiles * 100

Note:
- If only 1 platform is available, Popularity depends on it, but with a penalty in Multiplatform.

## 2) Recent growth
Input: metric delta between windows (e.g.: now vs 24h ago; now vs 7d average).
In the MVP:
- Growth = function of the ratio (value_now / max(eps, value_prev)) per platform, normalized in percentile.

Suggestion:
- growth_raw = log1p(value_now) - log1p(value_prev)
- growth_percentile per platform
- Growth = weighted average * 100

Fallback:
- If there is no history, use proxy: "novelty" (e.g.: many recent uploads on YouTube) with low weight.

## 3) Platform distribution
Goal: reward games with signals across multiple platforms.
Simple calculation (MVP):
- count_strong = number of platforms with percentile >= 0.70
- Distribution = min(100, count_strong * 35)
  - 1 strong platform: 35
  - 2 strong platforms: 70
  - 3+ strong platforms: 100

Optional (more elegant, V1):
- use entropy of percentiles per platform.

## 4) Channel compatibility
In the MVP, simple rule (no ML):
- Based on:
  - game genre (if available)
  - game keywords (tags) x channel keywords
  - channel blacklist/whitelist

MVP heuristic:
- fit = 50 base
- +10 if genre is in preferred_genres
- -20 if genre is in avoided_genres
- + (0..20) for match of keywords_positive
- - (0..20) for match of keywords_negative
Clamp 0..100.

Without game data:
- use name/aliases match with keywords (e.g.: "roguelike", "soulslike", "co-op").

## Explainability (required)
For each game in the top, record:
- platforms that drove the score (top 2)
- main metrics and deltas
- what was missing (missing_platforms)
- game match_confidence

## Recommended output
- Top 10 games
- For each game:
  - score_total + breakdown
  - trending platforms (strong/moderate/weak)
  - format recommendation (if there is a rule in the channel profile)
