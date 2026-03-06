# Logica de classificacao (MVP)

## Objetivo
Produzir um ranking de jogos para "gravar agora" que seja:
- explicavel (decomposicao por fatores)
- atual (considera recencia)
- multiplataforma (quando possivel)
- personalizavel (perfil do canal)

## Componentes do score (0..100)

ScoreTrending =
  w_pop  * Popularidade +
  w_grow * Crescimento +
  w_multi* DistribuicaoPorPlataforma +
  w_fit  * CompatibilidadeComCanal

Pesos sugeridos (MVP):
- w_pop = 0.40
- w_grow = 0.30
- w_multi = 0.20
- w_fit = 0.10 (ou 0 se nao houver perfil)

## 1) Popularidade geral
Entrada: metricas "nivel" por plataforma.
Exemplos:
- Twitch viewers (attention_viewers)
- YouTube views agregadas (attention_views)
- Steam players_current

Como normalizar:
- Para cada plataforma, calcular rank_percentile do jogo no snapshot.
- Popularidade = media ponderada dos percentis disponiveis * 100

Observacao:
- Se so 1 plataforma disponivel, Popularidade depende dela, mas com penalidade em Multiplataforma.

## 2) Crescimento recente
Entrada: delta de metricas entre janelas (ex.: agora vs 24h atras; agora vs 7d media).
No MVP:
- Crescimento = funcao do ratio (value_now / max(eps, value_prev)) por plataforma, normalizado em percentil.

Sugestao:
- growth_raw = log1p(value_now) - log1p(value_prev)
- growth_percentile por plataforma
- Crescimento = media ponderada * 100

Fallback:
- Se nao houver historico, usar proxy: "novidade" (ex.: muitos uploads recentes no YouTube) com peso baixo.

## 3) Distribuicao por plataforma
Objetivo: premiar jogos com sinal em varias plataformas.
Calculo simples (MVP):
- count_strong = numero de plataformas com percentile >= 0.70
- Distribuicao = min(100, count_strong * 35)
  - 1 plataforma forte: 35
  - 2 plataformas fortes: 70
  - 3+ plataformas fortes: 100

Opcional (mais elegante, V1):
- usar entropia dos percentis por plataforma.

## 4) Compatibilidade com o canal
No MVP, regra simples (sem ML):
- Baseado em:
  - genero do jogo (se disponivel)
  - keywords do jogo (tags) x keywords do canal
  - blacklist/whitelist do canal

Heuristica MVP:
- fit = 50 base
- +10 se genero esta em preferred_genres
- -20 se genero esta em avoided_genres
- + (0..20) por match de keywords_positive
- - (0..20) por match de keywords_negative
Clamp 0..100.

Sem dados do jogo:
- usar match de nome/aliases com keywords (ex.: "roguelike", "soulslike", "co-op").

## Explicabilidade (obrigatorio)
Para cada jogo no top, registrar:
- plataformas que puxaram a nota (top 2)
- principais metricas e deltas
- o que faltou (missing_platforms)
- match_confidence do jogo

## Saida recomendada
- Top 10 jogos
- Para cada jogo:
  - score_total + breakdown
  - plataformas em alta (forte/moderada/fraca)
  - recomendacao de formato (se houver regra no perfil do canal)