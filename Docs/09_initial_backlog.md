# Initial backlog (epics -> features -> tasks)

## Epic A: Project foundation
### Feature A1: Repository and standards
- Task: create base structure (src, tests, docs, scripts)
- Task: lint/format (ruff/black) and pre-commit
- Task: basic CI (unit tests)

### Feature A2: Config and secrets
- Task: load env vars (twitch/youtube keys)
- Task: channel_profile.yaml (schema)

---

## Epic B: Ingestion (collection)
### Feature B1: Twitch connector (Helix)
- Task: authenticate (client credentials)
- Task: collect top games
- Task: collect streams by game_id
- Task: save raw snapshot

### Feature B2: YouTube connector (Search + Videos)
- Task: search videos by term and time window
- Task: fetch stats by videoId
- Task: calculate aggregates per game
- Task: save raw snapshot

### Feature B3: Steam connector (current players)
- Task: query GetNumberOfCurrentPlayers by appid
- Task: save raw snapshot

### Feature B4: CSV import (TikTok/Instagram)
- Task: define CSV template
- Task: parser + validation
- Task: include in metrics model

---

## Epic C: Normalization and entity resolution
### Feature C1: Common metrics model
- Task: convert responses to PlatformMetric
- Task: persist PlatformMetric in SQLite

### Feature C2: Game matching (MVP)
- Task: manual aliases table
- Task: match by name (casefold + simple fuzzy)
- Task: store confidence

---

## Epic D: Scoring and recommendations
### Feature D1: Score calculation
- Task: normalization by platform (percentile)
- Task: growth by window (requires history)
- Task: score_multiplatform
- Task: score_fit (rules by profile)

### Feature D2: Explainability
- Task: explanation json (top signals, deltas, missing)

---

## Epic E: Interface (MVP)
### Feature E1: CLI
- Task: `ingest` (creates snapshot)
- Task: `score` (calculates)
- Task: `recommend` (shows ranking)

### Feature E2: API (optional MVP)
- Task: endpoint /trending
- Task: endpoint /recommendations

---

## Epic F: Operations and quality
### Feature F1: Lightweight observability
- Task: structured logs
- Task: execution metrics (duration, counts)

### Feature F2: Documentation
- Task: README with setup and examples
- Task: configuration docs and templates
