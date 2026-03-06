# Estrutura do repositorio GitHub (sugestao)

## Objetivo
Repo claro e padronizado, facil de rodar local e evoluir para servicos.

## Arvore (sugestao)

.
├─ docs/
├─ src/
│  ├─ app/
│  │  ├─ ingestion/
│  │  ├─ normalization/
│  │  ├─ scoring/
│  │  ├─ storage/
│  │  └─ api/               (opcional no MVP)
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

## Padroes
- src layout (evita import baguncado)
- config versionado (sem secrets)
- secrets via env vars
- docs com indice e decisoes

## Arquivos essenciais
- README.md: como rodar MVP em 5 minutos
- .env.example: lista de variaveis
- config/channel_profile.yaml: perfil do canal
- config/games_seed.yaml: lista inicial de jogos/appids (curada)

## Convencoes
- Sem scraping agressivo no MVP.
- Se um conector nao puder operar sem ToS/limites, vira "import manual" (CSV).