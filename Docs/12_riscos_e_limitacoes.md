# Riscos e limitacoes

## 1) Limitacoes de APIs e dados
- YouTube: nao ha "top jogos" oficial direto; usamos proxies via busca e agregacao.
- Steam: player count e por appid; nao ha lista oficial "top" via Web API.
- TikTok/Instagram: trending global nao e trivial via API; MVP depende de importacao manual.

Mitigacao:
- Transparencia na UI/explicacao: "este sinal e proxy".
- Modularizar conectores para evoluir sem reescrever core.

## 2) Quotas e rate limits
- YouTube search e caro em quota; risco de estourar.
Mitigacao:
- Limitar numero de jogos consultados (top N seed + top twitch).
- Cache por termo/janela e backoff.

## 3) Resolucao de entidades (nome do jogo)
- Ambiguidade de nomes, abreviacoes, traducoes.
Mitigacao:
- Alias manual para top N.
- Confidence score e penalidade quando baixo.
- Evoluir para fuzzy + base de IDs (V1).

## 4) Viés de plataforma
- Twitch favorece certos generos/formatos.
Mitigacao:
- Score_multiplataforma e pesos ajustaveis.
- Perfil do canal influencia recomendacao.

## 5) "Saturacao" vs "oportunidade"
- Jogo em alta pode estar saturado (muita oferta).
Mitigacao:
- Introduzir sinal de oferta (uploads/streams) e opcional penalidade por saturacao (V1).

## 6) Operacao
- Jobs falham, dados incompletos, snapshots faltando.
Mitigacao:
- Reprocessamento idempotente.
- Status partial + penalidade.

## 7) Compliance/ToS
- Scraping pode violar termos.
Mitigacao:
- MVP evita scraping agressivo; usa APIs oficiais e import manual.