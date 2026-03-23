# GitHub repository structure (suggestion)

## Goal
Clear and standardized repo, easy to run locally and evolve into services.

## Tree (suggestion)

.
├─ docs/
├─ src/
│  ├─ app/
│  │  ├─ ingestion/
│  │  ├─ normalization/
│  │  ├─ scoring/
│  │  ├─ storage/
│  │  └─ api/               (optional in MVP)
│  └─ main.py
├─ scripts/
├─ tests/
├─ config/
│  ├─ channel_profile.yaml
│  ├─ games_seed.yaml
│  └─ csv_templates/
├─ .env.example
├─ README.md
├─ pyproject.toml
└─ LICENSE

## Standards
- src layout (avoids messy imports)
- versioned config (no secrets)
- secrets via env vars
- docs with index and decisions

## Essential files
- README.md: how to run MVP in 5 minutes
- .env.example: list of variables
- config/channel_profile.yaml: channel profile
- config/games_seed.yaml: initial list of games/appids (curated)

## Conventions
- No aggressive scraping in the MVP.
- If a connector cannot operate without violating ToS/limits, it becomes a "manual import" (CSV).
