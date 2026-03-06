# Arquitetura proposta (texto/ASCII)

## Visao geral
Arquitetura modular com 3 camadas:
- Ingestion (conectores por plataforma)
- Core (normalizacao, resolucao de jogos, scoring)
- Serving (CLI/API)

## Diagrama ASCII (MVP)

+-------------------+        +---------------------+        +---------------------+
|  Schedulers/Jobs   |  --->  |   Ingestion Layer   |  --->  |   Normalization     |
|  (cron/actions)    |        | (twitch/youtube/    |        | + Entity Resolution |
+-------------------+        |  steam/csv_import)  |        +---------------------+
                                      |                               |
                                      v                               v
                              +----------------+              +------------------+
                              |   Raw Storage  |              |  Metrics Storage |
                              | (json blobs)   |              | (SQLite tables)  |
                              +----------------+              +------------------+
                                                                    |
                                                                    v
                                                            +---------------+
                                                            |   Scoring     |
                                                            | (per snapshot)|
                                                            +---------------+
                                                                    |
                                                                    v
                                                         +--------------------+
                                                         |   Recommendations  |
                                                         |  (rank + explain)  |
                                                         +--------------------+
                                                          /                \
                                                         v                  v
                                                 +--------------+   +----------------+
                                                 | CLI (MVP)    |   | API (optional) |
                                                 +--------------+   +----------------+

## Decisoes arquiteturais (MVP)
- Linguagem: Python (rapido para data e APIs).
- Persistencia: SQLite (simples, local, versionavel por migrations basicas).
- Jobs: execucao local via cron ou GitHub Actions (se quiser rodar em repo).
- Config: YAML para perfil do canal + chaves via env vars.

## Evolucao (V1)
- Separar servico de ingestion (fila) e API.
- Postgres e jobs com worker (ex.: Celery/RQ).
- Dashboard (Next.js) consumindo API.

## Evolucao (V2)
- Feature store + embeddings + recomendacao personalizada.
- Alertas e notificacoes.
- Multiusuario e multi-canais.