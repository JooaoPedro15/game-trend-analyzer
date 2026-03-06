# Fase 1 (scaffold) - sem travar decisoes

## Objetivo
Criar o esqueleto do MVP para rodar local:
- ingest -> persist -> score -> recommend

## Stack sugerida (MVP)
- Python 3.12+
- SQLite
- CLI (Typer) e opcional API (FastAPI)
- HTTP clients: httpx
- Config: pydantic-settings + YAML
- Qualidade: ruff + pytest

## Estrutura minima
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

## Fluxo do MVP
1) `cli ingest` cria snapshot e grava raw + metricas
2) `cli score` calcula scores e grava TrendScore
3) `cli recommend` imprime top N com breakdown

## Templates (MVP)
- config/games_seed.yaml: lista curada de (game_name, steam_appid, youtube_query_terms)
- config/channel_profile.yaml: preferencias e keywords

## Entregas de Fase 1 (primeiro MVP funcional)
- CLI funcionando com pelo menos Twitch (ingest + recommend)
- Persistencia SQLite
- Documentacao para rodar em 5 minutos