# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendGames is a local MVP that ingests gaming trend metrics from multiple platforms and recommends which games a content creator should cover next. Written in Python 3.12+ with **zero external dependencies** (stdlib only, including a custom YAML parser).

## Commands

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
export PYTHONPATH=src

# Run full pipeline (ingest → score → recommend)
python -m trendgames.cli run --top 10

# Run individual stages
python -m trendgames.cli ingest
python -m trendgames.cli score
python -m trendgames.cli recommend --top 10

# With real YouTube API data
python -m trendgames.cli run --youtube-api-key YOUR_KEY --top 10
# Or: export YOUTUBE_API_KEY=YOUR_KEY

# CSV import for manual metrics
python -m trendgames.cli ingest --csv config/csv_templates/metrics_import_template.csv

# Editable install (alternative to PYTHONPATH)
pip install -e .
trendgames run --top 10
```

There are currently no tests or linting configured.

## Architecture

**3-layer pipeline:** Ingestion → Scoring → Serving (CLI)

### Ingestion Layer (`src/trendgames/ingestion/`)
Platform connectors collect metrics into snapshots stored in SQLite. By default, connectors use **deterministic simulation** (SHA256-based reproducible fake data) for offline development. The `youtube_api.py` connector is the first real API integration (YouTube Data API v3) — it checks what games reference channels are covering.

### Scoring Layer (`src/trendgames/scoring.py`)
Calculates a composite trend score per game with four weighted components:
- **Popularity (40%)**: Percentile ranking per platform, averaged
- **Growth (30%)**: log1p delta vs previous snapshot, normalized
- **Multiplatform (20%)**: Count of "strong" platforms (≥70th percentile) × 35 points
- **Fit (0-10%)**: Tag match against channel preferences/avoided types from `config/channel_profile.yaml`

### Storage (`src/trendgames/storage.py`)
SQLite database at `data/trendgames.db`. Tables: `games`, `snapshots`, `platform_metrics`, `trend_scores`.

### Settings (`src/trendgames/settings.py`)
Custom pure-Python YAML parser (no PyYAML). Loads `config/channel_profile.yaml` (creator preferences, reference channels) and `config/games_seed.yaml` (candidate game list).

### Data Models (`src/trendgames/domain.py`)
Frozen dataclasses: `GameSeed`, `ChannelProfile`, `PlatformMetric`, `TrendScore`.

## Key Design Decisions

- **Zero dependencies**: All stdlib — custom YAML parser, urllib for HTTP, sqlite3 for storage.
- **Simulated data by default**: Allows full pipeline testing offline; real APIs are opt-in.
- **Snapshot-based**: Each `ingest` creates a timestamped snapshot for growth comparison.
- **Explainable scoring**: Each recommendation includes a breakdown of why it scored high.

## Configuration

- `config/channel_profile.yaml`: Creator profile (content types, preferred/avoided game types, reference channels)
- `config/games_seed.yaml`: List of candidate games with tags, steam_appid, and youtube_queries
- `.env` / `YOUTUBE_API_KEY`: YouTube Data API v3 key (optional)
