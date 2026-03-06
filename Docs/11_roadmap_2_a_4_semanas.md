# Roadmap (2 a 4 semanas)

## Semana 1 (fundacao + primeiro dado)
- Setup repo, lint, CI, docs base.
- Modelos iniciais (Game, Snapshot, PlatformMetric).
- Twitch connector: top games + persistir raw + normalizado.
- CLI: comando `ingest:twitch`.

Entrega ao fim da semana:
- Ranking simples so com Twitch (popularidade) para validar pipeline.

## Semana 2 (YouTube + Steam + historico)
- YouTube connector (busca por termo + stats) com cache simples.
- Steam connector (current players por appid).
- Persistencia em SQLite.
- Snapshots com historico (rodar 2-3x para gerar comparacao).

Entrega ao fim da semana:
- Score_popularity + score_growth (parcial) em 2-3 plataformas.

## Semana 3 (scoring completo + perfil do canal)
- Scoring completo (pop, grow, multi, fit).
- ChannelProfile via YAML + regras simples de fit.
- Explicabilidade (breakdown por jogo).
- CLI `recommend`.

Entrega ao fim da semana:
- MVP funcional via CLI.

## Semana 4 (polimento + opcional API)
- Melhorias de entity matching (aliases, confianca).
- Importacao CSV para TikTok/Instagram (opcional).
- API FastAPI minimal (opcional) + endpoint de recomendacoes.
- Documentacao final e exemplos.

Entrega ao fim da semana:
- MVP pronto para uso diario (local) e facil deploy.