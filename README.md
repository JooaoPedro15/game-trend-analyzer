# TrendGames — Game Scout para Criadores de Conteúdo Vertical

Ferramenta local para criadores de gameplay vertical (TikTok / YouTube Shorts / Instagram Reels) que ingere métricas de tendência de múltiplas plataformas e recomenda quais jogos cobrir a seguir.

**Canal alvo:** Roberto Careca — gameplay vertical PT-BR, nicho indie/puzzle/bizarro/horror.

## Requisitos

- Python 3.12+
- Sem dependências externas (stdlib only)
- YouTube Data API v3 key (opcional — necessária para cobertura real dos canais de referência)

## Setup

```bash
# Windows (Git Bash)
python -m venv .venv
source .venv/Scripts/activate
export PYTHONPATH=src

# Ou editable install
pip install -e .
```

## Uso Principal — Comando Scout

O comando `scout` gera um relatório no estilo Game Scout com scoring otimizado para conteúdo vertical:

```bash
# Modo offline (scoring por tags, sem API)
python -m trendgames.cli scout --top 10

# Com cobertura real dos canais YouTube de referência
python -m trendgames.cli scout --youtube-api-key YOUR_KEY --top 10
export YOUTUBE_API_KEY=YOUR_KEY
python -m trendgames.cli scout --top 10
```

**Exemplo de saída:**

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

**Fórmula de scoring:**
- Viral Vertical (40%) — tags WTF/horror/bizarro/puzzle + boost por cobertura dos canais
- Curiosidade (25%) — fator "para de scrollar"
- Funil p/ Vídeo Longo (20%) — potencial de virar vídeo longo após o short viralizar
- Facilidade de Produção (15%) — quão fácil gravar

**Urgência** baseada em cobertura dos canais YouTube de referência:
- `GRAVAR AGORA` — 2+ canais cobriram recentemente
- `GRAVAR ESSA SEMANA` — 1 canal cobriu
- `PODE PLANEJAR` — score ≥ 7.0, boa janela futura
- `FICAR DE OLHO` — monitorar

## Outros Comandos

```bash
# Pipeline genérico (popularity/growth/multiplatform/fit)
python -m trendgames.cli run --top 10
python -m trendgames.cli run --youtube-api-key YOUR_KEY --top 10

# Etapas individuais
python -m trendgames.cli ingest
python -m trendgames.cli score
python -m trendgames.cli recommend --top 10

# Importar métricas manuais via CSV (ex: cobertura TikTok registrada manualmente)
python -m trendgames.cli ingest --csv config/csv_templates/metrics_import_template.csv
```

## Configuração

| Arquivo | Descrição |
|---------|-----------|
| `config/channel_profile.yaml` | Perfil do criador, jogos preferidos/evitados, canais de referência YouTube e TikTok |
| `config/games_seed.yaml` | Lista de jogos candidatos com tags, steam_appid, youtube_queries |
| `.env` / `YOUTUBE_API_KEY` | YouTube Data API v3 key |

## Canais de Referência

### YouTube (cobertura real com `--youtube-api-key`)
@TexHS, @T3ddySQueGames, @capjoga, @DarkViperAU, @markiplier, @Sauceddie, @Jazzghost, @jacksepticeye, @CellbitLives, @alanzoka, @kksaiko, @SMii7Y

### TikTok (listados no config, sem API pública disponível)
@lohzao (prioridade #1), @cofflei, @elcamacho24, @matsukiiii0, @sev7njogos

> TikTok não tem API pública. Para registrar cobertura manual dos criadores TikTok,
> use `--csv` com o template em `config/csv_templates/metrics_import_template.csv`.

## Arquitetura

```
src/trendgames/
├── cli.py                    # Entry point — comandos: scout, run, ingest, score, recommend
├── domain.py                 # Dataclasses: GameSeed, ChannelProfile, PlatformMetric, TrendScore
├── scout_scoring.py          # Scoring vertical: Viral + Curiosidade + Funil + Produção
├── scoring.py                # Scoring genérico: Popularity + Growth + Multiplatform + Fit
├── storage.py                # SQLite (data/trendgames.db)
├── settings.py               # YAML parser customizado
└── ingestion/
    ├── youtube_api.py        # Real: YouTube Data API v3 (canais de referência)
    ├── tiktok_search.py      # Limitado: TikTok sem API pública
    ├── steam.py              # Simulado
    ├── twitch.py             # Simulado
    ├── youtube.py            # Simulado
    └── csv_import.py         # Import manual
```
