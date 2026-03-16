# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendGames é uma ferramenta local para criadores de conteúdo de gameplay vertical (TikTok/Shorts/Reels). Ingere métricas de tendência de múltiplas plataformas e recomenda quais jogos cobrir. Escrito em Python 3.12+ com **zero dependências externas** (stdlib only, incluindo YAML parser customizado).

**Canal alvo:** Roberto Careca — gameplay vertical PT-BR, nicho indie/puzzle/bizarro/horror.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
export PYTHONPATH=src

# Pipeline completo (ingest → score → recommend)
python -m trendgames.cli run --top 10

# Comando scout — relatório game-scout com scoring vertical
python -m trendgames.cli scout --top 10

# Scout com cobertura real dos canais YouTube de referência
python -m trendgames.cli scout --youtube-api-key YOUR_KEY --top 10
# Ou: export YOUTUBE_API_KEY=YOUR_KEY

# Comandos individuais
python -m trendgames.cli ingest
python -m trendgames.cli score
python -m trendgames.cli recommend --top 10

# CSV import para métricas manuais (ex: cobertura TikTok registrada manualmente)
python -m trendgames.cli ingest --csv config/csv_templates/metrics_import_template.csv

# Editable install (alternativa ao PYTHONPATH)
pip install -e .
trendgames scout --youtube-api-key YOUR_KEY --top 10
```

Não há testes ou linting configurados.

## Architecture

**3-layer pipeline:** Ingestion → Scoring → Serving (CLI)

### Ingestion Layer (`src/trendgames/ingestion/`)
Conectores coletam métricas em snapshots no SQLite. Por padrão usam **simulação determinística** (SHA256 reproduzível) para desenvolvimento offline.

| Arquivo | Plataforma | Descrição |
|---------|-----------|-----------|
| `twitch.py` | Twitch | Simulado |
| `youtube.py` | YouTube | Simulado |
| `steam.py` | Steam | Simulado |
| `youtube_api.py` | `reference_channels_youtube` | **Real** — YouTube Data API v3. Busca vídeos recentes dos canais de referência e conta cobertura por jogo. |
| `tiktok_search.py` | TikTok | **Limitado** — TikTok não tem API pública. Emite mensagem de limitação. Cobertura TikTok pode ser registrada manualmente via CSV. |
| `csv_import.py` | qualquer | Import manual de métricas via CSV |

### Scout Layer (`src/trendgames/scout_scoring.py`)
Fórmula otimizada para conteúdo vertical curto:
- **Viral Vertical (40%)**: tags WTF/horror/bizarro/puzzle + boost por cobertura dos canais de referência
- **Curiosidade (25%)**: tags curioso/WTF/bizarro/escape/puzzle
- **Funil p/ Vídeo Longo (20%)**: tags indie/narrativa/roguelite/cartas/horror
- **Facilidade de Produção (15%)**: tags casual/puzzle/satisfying vs shooter/moba/competitivo

Urgência baseada em `coverage_count` (cobertura pelos canais YouTube de referência):
- `coverage_count ≥ 2` → **GRAVAR AGORA**
- `coverage_count == 1` → **GRAVAR ESSA SEMANA**
- `score ≥ 7.0` → **PODE PLANEJAR**
- else → **FICAR DE OLHO**

### Scoring Layer (`src/trendgames/scoring.py`)
Scoring genérico (usado pelo `run`/`recommend`):
- **Popularity (40%)**: percentile ranking por plataforma
- **Growth (30%)**: log1p delta vs snapshot anterior
- **Multiplatform (20%)**: count de plataformas "fortes" (≥70th percentile) × 35
- **Fit (0-10%)**: match de tags contra preferências/evitados do `channel_profile.yaml`

### Storage (`src/trendgames/storage.py`)
SQLite em `data/trendgames.db`. Tabelas: `games`, `snapshots`, `platform_metrics`, `trend_scores`.

### Settings (`src/trendgames/settings.py`)
YAML parser puro Python (sem PyYAML). Carrega `config/channel_profile.yaml` e `config/games_seed.yaml`.

### Data Models (`src/trendgames/domain.py`)
Frozen dataclasses: `GameSeed`, `ChannelProfile`, `PlatformMetric`, `TrendScore`.
`ChannelProfile` tem dois campos de canais de referência:
- `reference_channels_youtube: list[str]` — handles YouTube (@markiplier, @alanzoka, etc.)
- `reference_channels_tiktok: list[str]` — handles TikTok (@lohzao, @cofflei, etc.) — listados no config mas cobertura real requer TikTok API

## Key Design Decisions

- **Zero dependencies**: Tudo stdlib — YAML parser customizado, urllib para HTTP, sqlite3 para storage.
- **Simulated data by default**: Pipeline completo funciona offline; APIs reais são opt-in.
- **Snapshot-based**: Cada `ingest` cria um snapshot timestamped para comparação de crescimento.
- **Dual scoring**: `recommend` usa scoring genérico de popularidade; `scout` usa scoring vertical.
- **TikTok limitation**: TikTok não tem API pública. Cobertura de criadores TikTok pode ser importada via CSV.

## Configuration

- `config/channel_profile.yaml`: Perfil do criador (Roberto Careca), tipos de jogo preferidos/evitados, canais de referência YouTube e TikTok
- `config/games_seed.yaml`: Lista de jogos candidatos com tags, steam_appid, youtube_queries
- `.env` / `YOUTUBE_API_KEY`: YouTube Data API v3 key (opcional, necessária para cobertura real dos canais YouTube)

## Canais de Referência

### YouTube (cobertura real com API key)
@TexHS, @T3ddySQueGames, @capjoga, @DarkViperAU, @markiplier, @Sauceddie, @Jazzghost, @jacksepticeye, @CellbitLives, @alanzoka, @kksaiko, @SMii7Y

### TikTok (listados no config, cobertura via CSV manual)
@lohzao (Lozão — prioridade #1), @cofflei, @elcamacho24, @matsukiiii0, @sev7njogos
