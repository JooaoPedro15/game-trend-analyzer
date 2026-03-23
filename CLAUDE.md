# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendGames is a local tool for vertical gameplay content creators (TikTok/Shorts/Reels). It ingests trend metrics from multiple platforms and recommends which games to cover. Written in Python 3.12+ with **zero external dependencies** (stdlib only, including a custom YAML parser).

**Target channel:** Roberto Careca — vertical gameplay PT-BR, indie/puzzle/weird/horror niche.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
export PYTHONPATH=src

# Full pipeline (ingest → score → recommend)
python -m trendgames.cli run --top 10

# Scout command — game-scout report with vertical scoring
python -m trendgames.cli scout --top 10

# Scout with real coverage from YouTube reference channels
python -m trendgames.cli scout --youtube-api-key YOUR_KEY --top 10
# Or: export YOUTUBE_API_KEY=YOUR_KEY

# Individual commands
python -m trendgames.cli ingest
python -m trendgames.cli score
python -m trendgames.cli recommend --top 10

# CSV import for manual metrics (e.g.: TikTok coverage recorded manually)
python -m trendgames.cli ingest --csv config/csv_templates/metrics_import_template.csv

# Editable install (alternative to PYTHONPATH)
pip install -e .
trendgames scout --youtube-api-key YOUR_KEY --top 10
```

No tests or linting are configured.

## Architecture

**3-layer pipeline:** Ingestion → Scoring → Serving (CLI)

### Ingestion Layer (`src/trendgames/ingestion/`)
Connectors collect metrics in snapshots into SQLite. By default they use **deterministic simulation** (reproducible SHA256) for offline development.

| File | Platform | Description |
|------|----------|-------------|
| `twitch.py` | Twitch | Simulated |
| `youtube.py` | YouTube | Simulated |
| `steam.py` | Steam | Simulated |
| `youtube_api.py` | `reference_channels_youtube` | **Real** — YouTube Data API v3. Fetches recent videos from reference channels and counts coverage per game. |
| `tiktok_search.py` | TikTok | **Limited** — TikTok has no public API. Emits a limitation message. TikTok coverage can be recorded manually via CSV. |
| `csv_import.py` | any | Manual metrics import via CSV |

### Scout Layer (`src/trendgames/scout_scoring.py`)
Formula optimized for short vertical content:
- **Viral Vertical (40%)**: WTF/horror/weird/puzzle tags + boost for reference channel coverage
- **Curiosity (25%)**: curious/WTF/weird/escape/puzzle tags
- **Funnel to Long Video (20%)**: indie/narrative/roguelite/cards/horror tags
- **Production Ease (15%)**: casual/puzzle/satisfying tags vs shooter/moba/competitive

Urgency based on `coverage_count` (coverage by YouTube reference channels):
- `coverage_count >= 2` → **GRAVAR AGORA**
- `coverage_count == 1` → **GRAVAR ESSA SEMANA**
- `score >= 7.0` → **PODE PLANEJAR**
- else → **FICAR DE OLHO**

### Scoring Layer (`src/trendgames/scoring.py`)
Generic scoring (used by `run`/`recommend`):
- **Popularity (40%)**: percentile ranking per platform
- **Growth (30%)**: log1p delta vs previous snapshot
- **Multiplatform (20%)**: count of "strong" platforms (>=70th percentile) × 35
- **Fit (0-10%)**: tag match against preferred/avoided from `channel_profile.yaml`

### Storage (`src/trendgames/storage.py`)
SQLite at `data/trendgames.db`. Tables: `games`, `snapshots`, `platform_metrics`, `trend_scores`.

### Settings (`src/trendgames/settings.py`)
Pure Python YAML parser (no PyYAML). Loads `config/channel_profile.yaml` and `config/games_seed.yaml`.

### Data Models (`src/trendgames/domain.py`)
Frozen dataclasses: `GameSeed`, `ChannelProfile`, `PlatformMetric`, `TrendScore`.
`ChannelProfile` has two reference channel fields:
- `reference_channels_youtube: list[str]` — YouTube handles (@markiplier, @alanzoka, etc.)
- `reference_channels_tiktok: list[str]` — TikTok handles (@lohzao, @cofflei, etc.) — listed in config but real coverage requires TikTok API

## Key Design Decisions

- **Zero dependencies**: Everything stdlib — custom YAML parser, urllib for HTTP, sqlite3 for storage.
- **Simulated data by default**: Full pipeline works offline; real APIs are opt-in.
- **Snapshot-based**: Each `ingest` creates a timestamped snapshot for growth comparison.
- **Dual scoring**: `recommend` uses generic popularity scoring; `scout` uses vertical scoring.
- **TikTok limitation**: TikTok has no public API. TikTok creator coverage can be imported via CSV.

## Configuration

- `config/channel_profile.yaml`: Creator profile (Roberto Careca), preferred/avoided game types, YouTube and TikTok reference channels
- `config/games_seed.yaml`: List of candidate games with tags, steam_appid, youtube_queries
- `.env` / `YOUTUBE_API_KEY`: YouTube Data API v3 key (optional, required for real coverage of YouTube channels)

## Reference Channels

### YouTube (real coverage with API key)
@TexHS, @T3ddySQueGames, @capjoga, @DarkViperAU, @markiplier, @Sauceddie, @Jazzghost, @jacksepticeye, @CellbitLives, @alanzoka, @kksaiko, @SMii7Y

### TikTok (listed in config, coverage via manual CSV)
@lohzao (Lozão — priority #1), @cofflei, @elcamacho24, @matsukiiii0, @sev7njogos
