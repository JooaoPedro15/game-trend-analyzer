# Backlog inicial (epics -> features -> tasks)

## Epic A: Fundacao do projeto
### Feature A1: Repositorio e padroes
- Task: criar estrutura base (src, tests, docs, scripts)
- Task: lint/format (ruff/black) e pre-commit
- Task: CI basico (unit tests)

### Feature A2: Config e secrets
- Task: carregar env vars (twitch/youtube keys)
- Task: channel_profile.yaml (schema)

---

## Epic B: Ingestion (coleta)
### Feature B1: Twitch connector (Helix)
- Task: autenticar (client credentials)
- Task: coletar top games
- Task: coletar streams por game_id
- Task: salvar raw snapshot

### Feature B2: YouTube connector (Search + Videos)
- Task: buscar videos por termo e janela de tempo
- Task: buscar stats por videoId
- Task: calcular agregados por jogo
- Task: salvar raw snapshot

### Feature B3: Steam connector (current players)
- Task: consultar GetNumberOfCurrentPlayers por appid
- Task: salvar raw snapshot

### Feature B4: CSV import (TikTok/Instagram)
- Task: definir template CSV
- Task: parser + validacao
- Task: incluir no modelo de metricas

---

## Epic C: Normalizacao e resolucao de entidades
### Feature C1: Modelo comum de metricas
- Task: converter respostas em PlatformMetric
- Task: persistir PlatformMetric no SQLite

### Feature C2: Game matching (MVP)
- Task: tabela de aliases manual
- Task: match por nome (casefold + fuzzy simples)
- Task: armazenar confidence

---

## Epic D: Scoring e recomendacao
### Feature D1: Calculo de scores
- Task: normalizacao por plataforma (percentil)
- Task: crescimento por janela (precisa historico)
- Task: score_multiplatform
- Task: score_fit (regras por profile)

### Feature D2: Explicabilidade
- Task: explanation json (top signals, deltas, missing)

---

## Epic E: Interface (MVP)
### Feature E1: CLI
- Task: `ingest` (gera snapshot)
- Task: `score` (calcula)
- Task: `recommend` (mostra ranking)

### Feature E2: API (opcional MVP)
- Task: endpoint /trending
- Task: endpoint /recommendations

---

## Epic F: Operacao e qualidade
### Feature F1: Observabilidade leve
- Task: logs estruturados
- Task: metricas de execucao (duracao, contagens)

### Feature F2: Documentacao
- Task: README com setup e exemplos
- Task: docs de configuracao e templates