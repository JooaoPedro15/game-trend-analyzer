# Estrategia de coleta e atualizacao

## Objetivo
Gerar recomendacoes atuais, comparaveis entre janelas (24h e 7d), com rastreabilidade e baixo custo de operacao.

## Conceito base
- Coletamos "snapshots" periodicos por plataforma.
- Persistimos:
  1) raw data (como veio)
  2) dados normalizados (modelo comum)
  3) scores calculados (por janela)

## Frequencia (MVP)
- Snapshots: a cada 6 horas (4x/dia).
- Recalculo de scores: apos cada snapshot.
- Relatorio "top recomendacoes": sob demanda (API/CLI) usando o ultimo score.

Por que 6h?
- Bom equilibrio entre "agora" e custo (quota e rate limit).
- Suficiente para detectar viradas no mesmo dia.

## Pipeline (MVP)
1) Seed de jogos candidatos
   - Lista curada (config) + top games do Twitch (auto).
2) Coleta por plataforma
   - Twitch: top games + streams por game_id
   - YouTube: search por termo + stats por video id
   - Steam: current_players por appid (para jogos com appid conhecido)
   - CSV imports (opcional): TikTok/Instagram
3) Normalizacao
   - Converter para metricas padrao: platform_metric
4) Resolucao de entidade (game matching)
   - Mapear "nome/plataforma" -> game_id canonical
   - Manter confianca do match
5) Persistencia
   - Armazenar snapshot + metricas + scores
6) Exposicao
   - API/CLI: ranking e explicacao do score

## Estrategia de atualizacao (V1)
- Scheduler (cron/GitHub Actions) + filas (se necessario).
- Cache de respostas por plataforma.
- Retentiva:
  - raw: 30 dias
  - normalizado: 180 dias
  - scores: 365 dias

## Qualidade de dados
- Deteccao de outliers (ex.: API retornou 0 para tudo).
- Reprocessamento idempotente (snapshot_id).
- Auditoria: log de execucao + contagem de itens por plataforma.

## Falhas e degradacao
- Se uma plataforma falhar, recalcular score com as disponiveis (com penalidade).
- Marcar o resultado com "data_freshness" e "missing_platforms".

## Privacidade e compliance
- Evitar dados pessoais.
- Usar somente dados agregados/publicos.
- Respeitar quotas e ToS das plataformas.