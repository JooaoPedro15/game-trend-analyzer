# Fontes de dados por plataforma (o que da para obter e o que exige alternativa)

## Principio
No MVP, priorizamos:
- APIs oficiais ou endpoints estaveis e permitidos.
- Dados publicos acessiveis sem scraping agressivo.
- Importacao manual quando nao houver API adequada.

---

## Twitch (API oficial - Helix)
### O que e possivel obter
- Top Games (categorias/jogos mais assistidos): rank e metrics agregadas do momento.
- Streams por game_id: viewers, quantidade de streams, lingua, tags.

### Como vira "jogo em alta"
- Popularidade: viewers do jogo.
- Crescimento: comparar viewers/streams com snapshots anteriores (ex.: 24h e 7d).
- Plataforma forte para sinal de "ao vivo".

### Observacoes
- Requer app registration, client_id, client_secret, token app.
- Boa cobertura para jogos "streamaveis".

---

## YouTube (API oficial - YouTube Data API v3)
### O que e possivel obter
- Search.list: buscar por termo (nome do jogo) e filtrar por data (publishedAfter).
- Videos.list: obter estatisticas (viewCount, likeCount) para os IDs retornados pela busca.
- Channels.list: (opcional) dados do canal do usuario, se integrarmos.

### Limites importantes
- Nao existe um endpoint oficial simples "top jogos do YouTube agora".
- Entao usamos proxies: volume de videos recentes + views agregadas via busca por termo.

### Como vira "jogo em alta"
- Popularidade: soma de views de videos recentes relacionados ao termo.
- Crescimento: diferenca entre janelas (ex.: ultimos 1d vs 7d) e comparacao de snapshots.

### Observacoes
- Quota: chamadas de search custam bastante; precisamos cache e limitar numero de jogos consultados.

---

## Steam (API oficial - Steam Web API / Steamworks Web API)
### O que e possivel obter
- GetNumberOfCurrentPlayers (por appid): numero de jogadores ativos agora.

### O que NAO vem pronto
- Lista oficial "top jogos" via Web API.
- Player count historico por appid (precisamos armazenar snapshots).

### Como vira "jogo em alta"
- Popularidade: current_players.
- Crescimento: comparar com snapshots anteriores.

### Observacoes
- Precisamos de uma lista inicial de appids (seed). No MVP, vamos:
  - Manter uma lista curada (manual) + opcionalmente enriquecer via Twitch top games (nome) e mapear para appid (com estrategia de resolucao).

---

## TikTok
### O que e possivel obter (oficial)
- Research API existe, mas tem elegibilidade restrita e processo de aprovacao.
- Para muitos criadores, nao sera disponivel no MVP.

### Alternativas para MVP
- Importacao manual (CSV) de sinais:
  - hashtags relacionadas ao jogo
  - views de videos do tema (quando disponivel via analytics)
- Uso do TikTok Creative Center (Trend Discovery) como fonte manual (sem prometer automatizacao).

### Como vira "jogo em alta"
- Popularidade/crescimento via sinais importados (ex.: rank de hashtags, crescimento de posts).

---

## Instagram
### O que e possivel obter (oficial)
- Instagram Graph API e focada em dados do proprio negocio/conta e busca de hashtags (com limitacoes).
- Nao entrega "trending global de jogos" de forma direta.

### Alternativas para MVP
- Importacao manual (CSV) com:
  - posts/reels sobre o jogo (contagem)
  - views/reach (se o usuario tiver)
- Sinais por hashtags (limitados e sujeitos a regras).

---

## Outras fontes (opcional, V1+)
- Google Trends (nao oficial via bibliotecas; risco de instabilidade).
- Reddit (API publica; bom para detectar buzz, mas exige NLP).
- Steam store/top sellers (muitas vezes via endpoints nao documentados; evitar no MVP).

---

## Resumo: o que entra no MVP
- Twitch: sim (API oficial).
- YouTube: sim (API oficial, com proxies).
- Steam: sim (player count por appid, lista curada).
- TikTok/Instagram: somente importacao manual (CSV) no MVP.