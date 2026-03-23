# Product Vision

## Problem
Content creators need to decide "which game to record now". Today this decision is usually based on guesswork, fragmented hype, and poor cross-platform visibility.

## Proposal
A platform that:
1) Identifies which games are trending right now.
2) Shows on which platforms each game is performing (YouTube, TikTok, Instagram, Twitch, Steam, etc).
3) Indicates whether the game is trending across multiple platforms or only one.
4) Cross-references this data with the channel profile to suggest which games have the highest chance of success for the creator.

## Target user
- Content creator (primarily gaming) who publishes on 1+ platforms and wants to quickly decide the next game/topic.

## Goals (what we want to optimize)
- Reduce decision time (from hours to minutes).
- Increase the chance of picking a game with good short-term demand.
- Make the recommendation rationale transparent (why this game? on which platforms? which signal drove the score?).
- Allow incremental iteration: simple MVP, robust V1, intelligent V2.

## Non-goals (for now)
- Predicting virality with high precision (this is difficult and depends on the creator).
- Complete coverage of all games and all platforms from day 1.
- Dependency on aggressive scraping or ToS violations.
- Full automation for platforms without adequate APIs (e.g.: global TikTok/Instagram trending) in the MVP.

## Product principles
- Simplicity: few signals, well explained.
- Transparency: score decomposed by factors.
- Multiplatform by design: even if the MVP has few sources, the model must support several.
- Frequent enough updates for decisions (doesn't need to be real-time in the MVP).

## Increment (MVP -> V1 -> V2)
### MVP (2-4 weeks)
- Ingest "good and accessible" signals (Twitch + YouTube via search + Steam player count for a list of games).
- Manual import (CSV) for TikTok/Instagram if the user wants.
- Simple and explainable scoring.
- Output via CLI and/or simple API.

### V1
- Better entity resolution (mapping names to IDs with fewer errors).
- Historical persistence (DB) and comparison by time windows.
- Simple dashboard.
- Channel profile with guided onboarding.

### V2
- Personalized recommendations (rules + embeddings + learning from channel history).
- Alerts (when a game crosses a threshold).
- Segmentation by country/language and niche.
- Format suggestions (short, live, review) by platform.
