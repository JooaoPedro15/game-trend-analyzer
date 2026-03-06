# Definicao clara: o que significa "jogo em alta"

## Definicao operacional (curto prazo)
Um jogo esta "em alta" se apresenta combinacao de:
- Popularidade atual (nivel): muitos sinais de atencao/agregados agora.
- Crescimento recente (velocidade): aumento relevante em uma janela curta.
- Presenca multiplataforma (largura): sinais aparecem em mais de uma plataforma (quando disponivel).
- Recencia: os sinais sao atuais (ex.: ultimas 24h / 7 dias) e nao so "classicos" historicos.

## Janelas de tempo padrao
- Curto: 24 horas (sensivel a viradas).
- Medio: 7 dias (mais estavel para decidir pauta).
No MVP, vamos priorizar 7 dias com um "boost" de 24h quando houver dados.

## Unidades de medida (sinais)
Sinais variam por plataforma, mas entram em 2 categorias:

1) Sinais de atencao (consumo)
- Twitch: viewers e numero de streams por jogo/categoria.
- YouTube: quantidade de videos recentes e views agregadas para o jogo (via busca por termo).
- Steam: jogadores atuais (GetNumberOfCurrentPlayers) para o appid do jogo.

2) Sinais de criacao (oferta/competicao)
- YouTube: quantidade de uploads recentes sobre o jogo (proxy de cobertura).
- Twitch: quantidade de canais/streams (proxy de saturacao + interesse).

## Regras para evitar falsos positivos
- Exigir um minimo de evidencia: ex. pelo menos 2 sinais relevantes OU 1 sinal muito forte.
- Normalizar por plataforma para comparar dentro da mesma plataforma (rank/percentil).
- Penalizar ambiguidade: jogos com nomes genericos (ex.: "Inside") precisam de confianca alta no mapeamento.

## Definicao formal (score)
"Em alta" = ScoreTrending >= T

Onde:
ScoreTrending = w_pop * Popularidade + w_grow * Crescimento + w_multi * Multiplataforma + w_fit * Compatibilidade

No MVP:
- w_fit pode ser simples (regras + keywords), e pode ate ser 0 se o usuario nao fornecer perfil.
- Multiplataforma e calculada com base nas plataformas com dados disponiveis.

## Threshold (T)
- MVP: T = 70/100 (ajustavel), com classificacao:
  - 85-100: muito em alta
  - 70-84: em alta
  - 50-69: monitorar
  - <50: baixo sinal