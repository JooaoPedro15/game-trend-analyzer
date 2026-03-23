# Initial data model (MVP)

## Model goal
- Support multiplatform.
- Store history via snapshots.
- Explain ranking (factors and contributions).

## Entities (conceptual)

### Game
- id (uuid or string)
- name (canonical)
- aliases (list)
- genres (list, optional)
- platforms (list, optional)
- metadata (json)

### Platform
- id (enum/string): twitch, youtube, steam, tiktok, instagram
- name

### Snapshot
- id
- collected_at (datetime)
- window_hint (optional): "6h"
- status (ok/partial/fail)
- source_versions (json)
- notes (text)

### PlatformMetric
- id
- snapshot_id
- game_id
- platform_id
- metric_type (enum):
  - attention_viewers
  - attention_views
  - creation_uploads
  - supply_streams
  - players_current
  - hashtag_rank
  - custom
- value (float)
- unit (string)
- dimensions (json) (e.g.: country, language)
- raw_ref (json) (original ids: video_id, twitch game_id, appid)
- confidence (0..1)

### TrendScore
- id
- snapshot_id
- game_id
- score_total (0..100)
- score_popularity (0..100)
- score_growth (0..100)
- score_multiplatform (0..100)
- score_fit (0..100)
- explanation (json) (top signals, deltas, strong/weak platforms)
- missing_platforms (list)

### ChannelProfile (MVP: manual)
- id
- channel_name
- primary_platform (youtube/tiktok/etc)
- language (pt-BR, en, etc)
- regions (list)
- content_formats (list): shorts, longform, live, review, guides
- preferred_genres (list)
- avoided_genres (list)
- audience_age (optional)
- keywords_positive (list)
- keywords_negative (list)
- history_signals (optional in MVP): games that performed well

## Relationships
- Game 1..N PlatformMetric
- Snapshot 1..N PlatformMetric
- Game 1..N TrendScore
- Snapshot 1..N TrendScore

## Persistence in MVP
Options:
A) SQLite (recommended): simple and queryable.
B) JSONL per snapshot: faster to implement, less queryable.

Recommendation: SQLite with simple tables and JSON for flexible fields.

## Game identity (resolution)
- canonical game_id
- match_confidence
- match_source (manual, twitch, steam, youtube)
In the MVP, start with:
- aliases table and manual mapping for top N games.
