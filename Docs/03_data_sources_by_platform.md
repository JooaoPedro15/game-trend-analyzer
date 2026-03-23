# Data sources by platform (what can be obtained and what requires an alternative)

## Principle
In the MVP, we prioritize:
- Official APIs or stable, permitted endpoints.
- Publicly accessible data without aggressive scraping.
- Manual import when no adequate API is available.

---

## Twitch (official API - Helix)
### What can be obtained
- Top Games (most-watched categories/games): rank and aggregated metrics at the moment.
- Streams by game_id: viewers, number of streams, language, tags.

### How it becomes "trending game"
- Popularity: game viewers.
- Growth: compare viewers/streams with previous snapshots (e.g.: 24h and 7d).
- Strong platform signal for "live" content.

### Notes
- Requires app registration, client_id, client_secret, app token.
- Good coverage for "streamable" games.

---

## YouTube (official API - YouTube Data API v3)
### What can be obtained
- Search.list: search by term (game name) and filter by date (publishedAfter).
- Videos.list: get statistics (viewCount, likeCount) for IDs returned by the search.
- Channels.list: (optional) user channel data, if we integrate.

### Important limits
- There is no simple official endpoint "top games on YouTube right now".
- So we use proxies: volume of recent videos + aggregated views via term search.

### How it becomes "trending game"
- Popularity: sum of views of recent videos related to the term.
- Growth: difference between windows (e.g.: last 1d vs 7d) and snapshot comparison.

### Notes
- Quota: search calls are quite expensive; we need caching and limit the number of games queried.

---

## Steam (official API - Steam Web API / Steamworks Web API)
### What can be obtained
- GetNumberOfCurrentPlayers (by appid): number of active players right now.

### What does NOT come ready
- Official "top games" list via Web API.
- Historical player count by appid (we need to store snapshots).

### How it becomes "trending game"
- Popularity: current_players.
- Growth: compare with previous snapshots.

### Notes
- We need an initial list of appids (seed). In the MVP, we will:
  - Maintain a curated (manual) list + optionally enrich via Twitch top games (name) and map to appid (with resolution strategy).

---

## TikTok
### What can be obtained (official)
- Research API exists, but has restricted eligibility and an approval process.
- For many creators, it will not be available in the MVP.

### Alternatives for MVP
- Manual import (CSV) of signals:
  - hashtags related to the game
  - video views on the topic (when available via analytics)
- Use of TikTok Creative Center (Trend Discovery) as a manual source (without promising automation).

### How it becomes "trending game"
- Popularity/growth via imported signals (e.g.: hashtag ranking, post growth).

---

## Instagram
### What can be obtained (official)
- Instagram Graph API is focused on own business/account data and hashtag searches (with limitations).
- Does not deliver "global gaming trends" directly.

### Alternatives for MVP
- Manual import (CSV) with:
  - posts/reels about the game (count)
  - views/reach (if the user has them)
- Signals via hashtags (limited and subject to rules).

---

## Other sources (optional, V1+)
- Google Trends (unofficial via libraries; risk of instability).
- Reddit (public API; good for detecting buzz, but requires NLP).
- Steam store/top sellers (often via undocumented endpoints; avoid in MVP).

---

## Summary: what goes into the MVP
- Twitch: yes (official API).
- YouTube: yes (official API, with proxies).
- Steam: yes (player count by appid, curated list).
- TikTok/Instagram: manual import only (CSV) in the MVP.
