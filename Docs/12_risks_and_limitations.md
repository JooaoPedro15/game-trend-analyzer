# Risks and limitations

## 1) API and data limitations
- YouTube: there is no direct official "top games" endpoint; we use proxies via search and aggregation.
- Steam: player count is by appid; there is no official "top" list via Web API.
- TikTok/Instagram: global trending is not trivial via API; MVP depends on manual import.

Mitigation:
- Transparency in the UI/explanation: "this signal is a proxy".
- Modularize connectors to evolve without rewriting the core.

## 2) Quotas and rate limits
- YouTube search is expensive in quota; risk of exceeding it.
Mitigation:
- Limit the number of games queried (top N seed + top twitch).
- Cache by term/window and backoff.

## 3) Entity resolution (game name)
- Ambiguity of names, abbreviations, translations.
Mitigation:
- Manual alias for top N.
- Confidence score and penalty when low.
- Evolve to fuzzy + ID database (V1).

## 4) Platform bias
- Twitch favors certain genres/formats.
Mitigation:
- score_multiplatform and adjustable weights.
- Channel profile influences recommendation.

## 5) "Saturation" vs "opportunity"
- A trending game may be saturated (too much supply).
Mitigation:
- Introduce supply signal (uploads/streams) and optional saturation penalty (V1).

## 6) Operations
- Jobs fail, incomplete data, missing snapshots.
Mitigation:
- Idempotent reprocessing.
- Partial status + penalty.

## 7) Compliance/ToS
- Scraping may violate terms.
Mitigation:
- MVP avoids aggressive scraping; uses official APIs and manual import.
