# Clear definition: what does "trending game" mean

## Operational definition (short term)
A game is "trending" if it presents a combination of:
- Current popularity (level): many attention signals/aggregates right now.
- Recent growth (velocity): relevant increase within a short window.
- Multiplatform presence (breadth): signals appear on more than one platform (when available).
- Recency: the signals are current (e.g.: last 24h / 7 days) and not just historical "classics".

## Default time windows
- Short: 24 hours (sensitive to sudden shifts).
- Medium: 7 days (more stable for scheduling decisions).
In the MVP, we will prioritize 7 days with a 24h "boost" when data is available.

## Units of measurement (signals)
Signals vary by platform, but fall into 2 categories:

1) Attention signals (consumption)
- Twitch: viewers and number of streams per game/category.
- YouTube: quantity of recent videos and aggregated views for the game (via term search).
- Steam: current players (GetNumberOfCurrentPlayers) for the game's appid.

2) Creation signals (supply/competition)
- YouTube: number of recent uploads about the game (proxy for coverage).
- Twitch: number of channels/streams (proxy for saturation + interest).

## Rules to avoid false positives
- Require a minimum of evidence: e.g. at least 2 relevant signals OR 1 very strong signal.
- Normalize by platform to compare within the same platform (rank/percentile).
- Penalize ambiguity: games with generic names (e.g.: "Inside") need high confidence in the mapping.

## Formal definition (score)
"Trending" = ScoreTrending >= T

Where:
ScoreTrending = w_pop * Popularity + w_grow * Growth + w_multi * Multiplatform + w_fit * Compatibility

In the MVP:
- w_fit can be simple (rules + keywords), and can even be 0 if the user doesn't provide a profile.
- Multiplatform is calculated based on platforms with available data.

## Threshold (T)
- MVP: T = 70/100 (adjustable), with classification:
  - 85-100: very trending
  - 70-84: trending
  - 50-69: monitor
  - <50: low signal
