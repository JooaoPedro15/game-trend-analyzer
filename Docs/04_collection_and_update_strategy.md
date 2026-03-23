# Collection and update strategy

## Goal
Generate current recommendations, comparable across windows (24h and 7d), with traceability and low operating cost.

## Base concept
- We collect periodic "snapshots" per platform.
- We persist:
  1) raw data (as received)
  2) normalized data (common model)
  3) calculated scores (per window)

## Frequency (MVP)
- Snapshots: every 6 hours (4x/day).
- Score recalculation: after each snapshot.
- "Top recommendations" report: on demand (API/CLI) using the latest score.

Why 6h?
- Good balance between "now" and cost (quota and rate limit).
- Sufficient to detect shifts within the same day.

## Pipeline (MVP)
1) Seed of candidate games
   - Curated list (config) + top games from Twitch (auto).
2) Collection by platform
   - Twitch: top games + streams by game_id
   - YouTube: search by term + stats by video id
   - Steam: current_players by appid (for games with known appid)
   - CSV imports (optional): TikTok/Instagram
3) Normalization
   - Convert to standard metrics: platform_metric
4) Entity resolution (game matching)
   - Map "name/platform" -> canonical game_id
   - Maintain match confidence
5) Persistence
   - Store snapshot + metrics + scores
6) Exposure
   - API/CLI: ranking and score explanation

## Update strategy (V1)
- Scheduler (cron/GitHub Actions) + queues (if needed).
- Response cache per platform.
- Retention:
  - raw: 30 days
  - normalized: 180 days
  - scores: 365 days

## Data quality
- Outlier detection (e.g.: API returned 0 for everything).
- Idempotent reprocessing (snapshot_id).
- Audit: execution log + item count per platform.

## Failures and degradation
- If a platform fails, recalculate score with the available ones (with penalty).
- Mark the result with "data_freshness" and "missing_platforms".

## Privacy and compliance
- Avoid personal data.
- Use only aggregated/public data.
- Respect platform quotas and ToS.
