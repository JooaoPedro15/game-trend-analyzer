# TrendGames — Game Scout for Vertical Content Creators

Local tool for vertical gameplay creators (TikTok / YouTube Shorts / Instagram Reels) that ingests trend metrics from multiple platforms and recommends which games to cover next.

**Target channel:** Roberto Careca — vertical gameplay PT-BR, indie/puzzle/weird/horror niche.

## Requirements

- Python 3.12+
- No external dependencies (stdlib only)
- YouTube Data API v3 key (optional — required for real coverage of reference channels)

## Setup

```bash
# Windows (Git Bash)
python -m venv .venv
source .venv/Scripts/activate
export PYTHONPATH=src

# Or editable install
pip install -e .
```

## Main Usage — Scout Command

The `scout` command generates a Game Scout-style report with scoring optimized for vertical content:

```bash
# Offline mode (tag-based scoring, no API)
python -m trendgames.cli scout --top 10

# With real coverage from YouTube reference channels
python -m trendgames.cli scout --youtube-api-key YOUR_KEY --top 10
export YOUTUBE_API_KEY=YOUR_KEY
python -m trendgames.cli scout --top 10
```

**Example output:**

```
========================================================
  RELATORIO GAME SCOUT -- Roberto Careca
  Data: 2026-03-16  |  Canais checados: 17
========================================================

CANAIS CHECADOS:
  TikTok: @lohzao, @cofflei, @elcamacho24, @matsukiiii0, @sev7njogos
  YouTube: @markiplier, @CellbitLives, @alanzoka, @kksaiko ...

TOP JOGOS -- Rankeados por Score Game Scout
------------------------------------------------------------------------------
  # | Jogo                    | Cob. | TikTok | Shorts | Reels | Score | Urgencia
------------------------------------------------------------------------------
  1 | Buckshot Roulette       |    2 |    80% |    60% |   55% |   9.2 | GRAVAR AGORA
  2 | Content Warning         |    1 |    80% |    60% |   55% |   8.0 | GRAVAR ESSA SEMANA
  3 | Inscryption             |    0 |    70% |    90% |   75% |   6.8 | PODE PLANEJAR
```

**Scoring formula:**
- Viral Vertical (40%) — WTF/horror/weird/puzzle tags + boost for channel coverage
- Curiosity (25%) — "stop scrolling" factor
- Funnel to Long Video (20%) — potential to become a long video after the short goes viral
- Production Ease (15%) — how easy it is to record

**Urgency** based on coverage from YouTube reference channels:
- `GRAVAR AGORA` — 2+ channels covered recently
- `GRAVAR ESSA SEMANA` — 1 channel covered
- `PODE PLANEJAR` — score >= 7.0, good future window
- `FICAR DE OLHO` — monitor

## Other Commands

```bash
# Generic pipeline (popularity/growth/multiplatform/fit)
python -m trendgames.cli run --top 10
python -m trendgames.cli run --youtube-api-key YOUR_KEY --top 10

# Individual steps
python -m trendgames.cli ingest
python -m trendgames.cli score
python -m trendgames.cli recommend --top 10

# Import manual metrics via CSV (e.g.: TikTok coverage recorded manually)
python -m trendgames.cli ingest --csv config/csv_templates/metrics_import_template.csv
```

## Configuration

| File | Description |
|------|-------------|
| `config/channel_profile.yaml` | Creator profile, preferred/avoided games, YouTube and TikTok reference channels |
| `config/games_seed.yaml` | List of candidate games with tags, steam_appid, youtube_queries |
| `.env` / `YOUTUBE_API_KEY` | YouTube Data API v3 key |

## Reference Channels

### YouTube (real coverage with `--youtube-api-key`)
@TexHS, @T3ddySQueGames, @capjoga, @DarkViperAU, @markiplier, @Sauceddie, @Jazzghost, @jacksepticeye, @CellbitLives, @alanzoka, @kksaiko, @SMii7Y

### TikTok (listed in config, no public API available)
@lohzao (priority #1), @cofflei, @elcamacho24, @matsukiiii0, @sev7njogos

> TikTok has no public API. To record manual coverage from TikTok creators,
> use `--csv` with the template at `config/csv_templates/metrics_import_template.csv`.

## Architecture

```
src/trendgames/
├── cli.py                    # Entry point — commands: scout, run, ingest, score, recommend
├── domain.py                 # Dataclasses: GameSeed, ChannelProfile, PlatformMetric, TrendScore
├── scout_scoring.py          # Vertical scoring: Viral + Curiosity + Funnel + Production
├── scoring.py                # Generic scoring: Popularity + Growth + Multiplatform + Fit
├── storage.py                # SQLite (data/trendgames.db)
├── settings.py               # Custom YAML parser
└── ingestion/
    ├── youtube_api.py        # Real: YouTube Data API v3 (reference channels)
    ├── tiktok_search.py      # Limited: TikTok without public API
    ├── steam.py              # Simulated
    ├── twitch.py             # Simulated
    ├── youtube.py            # Simulated
    └── csv_import.py         # Manual import
```
