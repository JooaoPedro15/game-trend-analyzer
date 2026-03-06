# Visao do produto

## Problema
Criadores de conteudo precisam decidir "qual jogo gravar agora". Hoje essa decisao costuma ser baseada em achismo, hype fragmentado e pouca visibilidade multiplataforma.

## Proposta
Uma plataforma que:
1) Identifica quais jogos estao em alta agora.
2) Mostra em quais plataformas cada jogo esta performando (YouTube, TikTok, Instagram, Twitch, Steam, etc).
3) Indica se o jogo esta em alta em varias plataformas ou apenas em uma.
4) Cruza esses dados com o perfil do canal para sugerir quais jogos tem maior chance de dar certo para o criador.

## Usuario alvo
- Criador de conteudo (principalmente gaming) que publica em 1+ plataformas, e quer decidir rapidamente o proximo jogo/tema.

## Objetivos (o que queremos otimizar)
- Diminuir tempo de decisao (de horas para minutos).
- Aumentar chance de acertar um jogo com boa demanda no curto prazo.
- Tornar a justificativa da recomendacao transparente (por que esse jogo? em quais plataformas? qual sinal puxou a nota?).
- Permitir iteracao incremental: MVP simples, V1 robusto, V2 inteligente.

## Nao-objetivos (por enquanto)
- Prever viralizacao com alta precisao (isso e dificil e depende do criador).
- Cobertura completa de todos os jogos e todas as plataformas desde o dia 1.
- Dependencia de scraping agressivo ou violacao de ToS.
- Automacao total para plataformas sem APIs adequadas (ex.: trending global do TikTok/Instagram) no MVP.

## Principios de produto
- Simplicidade: poucos sinais, bem explicados.
- Transparencia: score decomposto por fatores.
- Multiplataforma por design: mesmo que o MVP tenha poucas fontes, o modelo deve suportar varias.
- Atualizacao frequente o suficiente para decisoes (nao precisa ser real-time no MVP).

## Incremento (MVP -> V1 -> V2)
### MVP (2-4 semanas)
- Ingerir sinais "bons e acessiveis" (Twitch + YouTube via busca + Steam player count para uma lista de jogos).
- Importacao manual (CSV) para TikTok/Instagram se o usuario quiser.
- Scoring simples e explicavel.
- Saida via CLI e/ou API simples.

### V1
- Melhor resolucao de entidades (mapear nomes para IDs com menos erro).
- Persistencia historica (DB) e comparacao por janelas de tempo.
- Dashboard simples.
- Perfil do canal com onboarding guiado.

### V2
- Recomendacao personalizada (regras + embeddings + aprendizado com historico do canal).
- Alertas (quando um jogo cruza um limiar).
- Segmentacao por pais/idioma e nicho.
- Sugestao de formatos (short, live, review) por plataforma.