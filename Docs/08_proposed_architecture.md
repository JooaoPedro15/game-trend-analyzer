# Proposed architecture (text/ASCII)

## Overview
Modular architecture with 3 layers:
- Ingestion (connectors per platform)
- Core (normalization, game resolution, scoring)
- Serving (CLI/API)

## ASCII diagram (MVP)

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

## Architectural decisions (MVP)
- Language: Python (fast for data and APIs).
- Persistence: SQLite (simple, local, versionable with basic migrations).
- Jobs: local execution via cron or GitHub Actions (if you want to run in a repo).
- Config: YAML for channel profile + keys via env vars.

## Evolution (V1)
- Separate ingestion service (queue) and API.
- Postgres and jobs with a worker (e.g.: Celery/RQ).
- Dashboard (Next.js) consuming API.

## Evolution (V2)
- Feature store + embeddings + personalized recommendations.
- Alerts and notifications.
- Multi-user and multi-channel.
