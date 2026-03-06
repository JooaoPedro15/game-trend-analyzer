# Modelo de dados inicial (MVP)

## Objetivo do modelo
- Suportar multiplataforma.
- Guardar historico por snapshots.
- Explicar ranking (fatores e contribuicoes).

## Entidades (conceitual)

### Game
- id (uuid ou string)
- name (canonical)
- aliases (lista)
- genres (lista, opcional)
- platforms (lista, opcional)
- metadata (json)

### Platform
- id (enum/string): twitch, youtube, steam, tiktok, instagram
- name

### Snapshot
- id
- collected_at (datetime)
- window_hint (opcional): "6h"
- status (ok/partial/fail)
- source_versions (json)
- notes (text)

### PlatformMetric
- id
- snapshot_id
- game_id
- platform_id
- metric_type (enum):
  - attention_viewers
  - attention_views
  - creation_uploads
  - supply_streams
  - players_current
  - hashtag_rank
  - custom
- value (float)
- unit (string)
- dimensions (json) (ex.: country, language)
- raw_ref (json) (ids originais: video_id, game_id twitch, appid)
- confidence (0..1)

### TrendScore
- id
- snapshot_id
- game_id
- score_total (0..100)
- score_popularity (0..100)
- score_growth (0..100)
- score_multiplatform (0..100)
- score_fit (0..100)
- explanation (json) (top signals, deltas, plataformas fortes/fracas)
- missing_platforms (lista)

### ChannelProfile (MVP: manual)
- id
- channel_name
- primary_platform (youtube/tiktok/etc)
- language (pt-BR, en, etc)
- regions (lista)
- content_formats (lista): shorts, longform, live, review, guides
- preferred_genres (lista)
- avoided_genres (lista)
- audience_age (opcional)
- keywords_positive (lista)
- keywords_negative (lista)
- history_signals (opcional no MVP): jogos que performaram bem

## Relacionamentos
- Game 1..N PlatformMetric
- Snapshot 1..N PlatformMetric
- Game 1..N TrendScore
- Snapshot 1..N TrendScore

## Persistencia no MVP
Opcoes:
A) SQLite (recomendado): simples e consultavel.
B) JSONL por snapshot: mais rapido de implementar, menos consultavel.

Recomendacao: SQLite com tabelas simples e JSON para campos flexiveis.

## Identidade do jogo (resolucao)
- game_id canonical
- match_confidence
- match_source (manual, twitch, steam, youtube)
No MVP, comecar com:
- tabela de aliases e mapeamento manual dos top N jogos.