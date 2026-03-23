# MVP Scope (and what is out of scope)

## MVP: definition
A "decision assistant" that delivers an explainable ranking of trending games and recommends those most aligned with the channel.

### MVP deliverables (functional)
1) Automatic collection:
   - Twitch: top games + streams (official)
   - YouTube: search by terms (official)
   - Steam: player count by appid (official)
2) Manual import (optional):
   - TikTok/Instagram via CSV (template provided)
3) Normalization and persistence:
   - snapshots + metrics + scores (SQLite recommended)
4) Ranking and explanation:
   - CLI: `recommend` to generate top games
   - Simple API (optional): endpoint to query the ranking
5) Channel profile (manual):
   - config file (YAML/JSON)

### What does NOT go into the MVP
- Full web dashboard (can be V1).
- Login, multi-user, teams.
- Automatic collection of TikTok/Instagram trending (without promising an API).
- Advanced ML for fit (embeddings, training, etc).
- Perfect entity resolution (we will improve iteratively).

## Success criteria (MVP)
- Can generate top 10 in < 2 minutes locally.
- Explains why each game appeared.
- Updates at least 4x/day.
- Allows adjusting the channel profile and seeing the change in ranking.

## Definition of Done (DoD)
- A command (or endpoint) that returns ranking + breakdown.
- Snapshot logs and idempotency.
- Documentation on how to run locally.
- Config and CSV templates.
