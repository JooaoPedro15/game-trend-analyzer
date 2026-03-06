# Escopo do MVP (e o que fica fora)

## MVP: definicao
Um "assistente de decisao" que entrega um ranking explicavel dos jogos em alta e recomenda os mais alinhados ao canal.

### Entregas MVP (funcional)
1) Coleta automatica:
   - Twitch: top games + streams (oficial)
   - YouTube: busca por termos (oficial)
   - Steam: player count por appid (oficial)
2) Importacao manual (opcional):
   - TikTok/Instagram via CSV (template fornecido)
3) Normalizacao e persistencia:
   - snapshots + metricas + scores (SQLite recomendado)
4) Ranking e explicacao:
   - CLI: `recommend` para gerar top jogos
   - API simples (opcional): endpoint para consultar o ranking
5) Perfil do canal (manual):
   - arquivo de config (YAML/JSON)

### O que NAO entra no MVP
- Dashboard web completo (pode ser V1).
- Login, multiusuario, times.
- Coleta automatica de TikTok/Instagram trending (sem prometer API).
- ML avançado para fit (embeddings, treinamento, etc).
- Resolucao perfeita de entidade (vamos melhorar iterativamente).

## Criterios de sucesso (MVP)
- Consegue gerar top 10 em < 2 minutos local.
- Explica por que cada jogo apareceu.
- Atualiza ao menos 4x/dia.
- Permite ajustar perfil do canal e ver mudanca no ranking.

## Definicao de pronto (DoD)
- Um comando (ou endpoint) que retorna ranking + breakdown.
- Logs e idempotencia do snapshot.
- Documentacao de como rodar local.
- Templates de config e CSV.