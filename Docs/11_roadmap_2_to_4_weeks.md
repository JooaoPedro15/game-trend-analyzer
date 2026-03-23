# Roadmap (2 to 4 weeks)

## Week 1 (foundation + first data)
- Set up repo, lint, CI, base docs.
- Initial models (Game, Snapshot, PlatformMetric).
- Twitch connector: top games + persist raw + normalized.
- CLI: `ingest:twitch` command.

Delivery at end of week:
- Simple ranking with Twitch only (popularity) to validate the pipeline.

## Week 2 (YouTube + Steam + history)
- YouTube connector (search by term + stats) with simple cache.
- Steam connector (current players by appid).
- Persistence in SQLite.
- Snapshots with history (run 2-3x to generate comparison).

Delivery at end of week:
- score_popularity + score_growth (partial) across 2-3 platforms.

## Week 3 (complete scoring + channel profile)
- Complete scoring (pop, grow, multi, fit).
- ChannelProfile via YAML + simple fit rules.
- Explainability (breakdown per game).
- CLI `recommend`.

Delivery at end of week:
- Functional MVP via CLI.

## Week 4 (polish + optional API)
- Entity matching improvements (aliases, confidence).
- CSV import for TikTok/Instagram (optional).
- Minimal FastAPI API (optional) + recommendations endpoint.
- Final documentation and examples.

Delivery at end of week:
- MVP ready for daily use (local) and easy to deploy.
