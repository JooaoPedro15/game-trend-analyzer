# Phase 1 (scaffold) - without locking in decisions

## Goal
Create the MVP skeleton to run locally:
- ingest -> persist -> score -> recommend

## Suggested stack (MVP)
- Python 3.12+
- SQLite
- CLI (Typer) and optional API (FastAPI)
- HTTP clients: httpx
- Config: pydantic-settings + YAML
- Quality: ruff + pytest

## Minimum structure
.
├─ src/app/
│  ├─ ingestion/        (twitch.py, youtube.py, steam.py)
│  ├─ storage/          (sqlite.py)
│  ├─ scoring/          (scorer.py)
│  ├─ domain/           (models.py)
│  └─ cli.py
├─ config/
│  ├─ channel_profile.yaml
│  └─ games_seed.yaml
├─ scripts/
│  └─ run_local.sh
├─ tests/
└─ README.md

## MVP flow
1) `cli ingest` creates a snapshot and saves raw + metrics
2) `cli score` calculates scores and saves TrendScore
3) `cli recommend` prints top N with breakdown

## Templates (MVP)
- config/games_seed.yaml: curated list of (game_name, steam_appid, youtube_query_terms)
- config/channel_profile.yaml: preferences and keywords

## Phase 1 deliverables (first functional MVP)
- CLI working with at least Twitch (ingest + recommend)
- SQLite persistence
- Documentation to run in 5 minutes
