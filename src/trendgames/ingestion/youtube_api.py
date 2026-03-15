from __future__ import annotations

import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric

_YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
_CHANNEL_URL_SUFFIXES = ("/videos", "/shorts", "/playlists", "/community", "/about", "/channels")


def collect_reference_channel_metrics(
    channels: Sequence[str],
    games: Sequence[GameSeed],
    api_key: str,
    collected_at: datetime,
    max_videos_per_channel: int = 50,
) -> list[CollectedMetric]:
    """Fetch recent videos from reference channels and count how many cover each game."""
    if not channels or not api_key:
        return []

    game_coverage: dict[str, int] = {game.game_id: 0 for game in games}
    game_lookup = _build_game_lookup(games)
    channels_ok = 0

    for channel in channels:
        try:
            channel_id = _resolve_channel_id(channel, api_key)
            if not channel_id:
                print(f"  [youtube_api] Could not resolve channel: {channel}")
                continue
            titles = _fetch_recent_video_titles(channel_id, api_key, max_videos_per_channel)
            for title in titles:
                game_id = _match_title_to_game(title, game_lookup)
                if game_id:
                    game_coverage[game_id] += 1
            channels_ok += 1
        except Exception as exc:
            print(f"  [youtube_api] Error fetching {channel}: {exc}")

    if channels_ok == 0:
        return []

    return [
        CollectedMetric(
            game_id=game.game_id,
            game_name=game.name,
            platform="reference_channels_youtube",
            metric_type="coverage_count",
            value=float(game_coverage.get(game.game_id, 0)),
            unit="videos",
            raw={"source": "youtube_api", "channels_analyzed": channels_ok},
        )
        for game in games
    ]


def _build_game_lookup(games: Sequence[GameSeed]) -> dict[str, str]:
    """Map normalized name variants -> game_id for title matching."""
    lookup: dict[str, str] = {}
    for game in games:
        _add_if_nonempty(lookup, _normalize(game.name), game.game_id)
        for query in game.youtube_queries:
            _add_if_nonempty(lookup, _normalize(query), game.game_id)
        # Short name alias: first significant word (len >= 4) to avoid false matches
        first_word = game.name.split()[0]
        if len(first_word) >= 4:
            _add_if_nonempty(lookup, _normalize(first_word), game.game_id)
    return lookup


def _add_if_nonempty(lookup: dict[str, str], key: str, value: str) -> None:
    if key and key not in lookup:
        lookup[key] = value


def _resolve_channel_id(channel_input: str, api_key: str) -> str | None:
    """Resolve a handle (@foo), URL, or bare channel ID to a YouTube channel ID."""
    stripped = channel_input.strip()

    # Strip known channel page suffixes (e.g. /videos, /shorts)
    for suffix in _CHANNEL_URL_SUFFIXES:
        if stripped.endswith(suffix):
            stripped = stripped[: -len(suffix)]
            break

    # Already a channel ID (starts with UC, 24 chars total)
    if re.match(r"^UC[\w-]{22}$", stripped):
        return stripped

    # Extract last path segment from URLs
    if "/" in stripped:
        stripped = stripped.rstrip("/").rsplit("/", 1)[-1]

    handle = stripped.lstrip("@")

    # Try forHandle (modern @handles)
    data = _api_get(_build_url("channels", {"forHandle": f"@{handle}", "part": "id", "key": api_key}))
    if data and data.get("items"):
        return data["items"][0]["id"]

    # Fallback: forUsername (legacy channels)
    data = _api_get(_build_url("channels", {"forUsername": handle, "part": "id", "key": api_key}))
    if data and data.get("items"):
        return data["items"][0]["id"]

    return None


def _fetch_recent_video_titles(channel_id: str, api_key: str, max_results: int) -> list[str]:
    """Return titles of the most recent videos from a channel."""
    data = _api_get(_build_url("search", {
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "type": "video",
        "maxResults": min(max_results, 50),
        "key": api_key,
    }))
    if not data:
        return []
    return [
        item["snippet"]["title"]
        for item in data.get("items", [])
        if item.get("snippet", {}).get("title")
    ]


def _match_title_to_game(title: str, lookup: dict[str, str]) -> str | None:
    """Return the first game_id whose name appears in the video title."""
    normalized = _normalize(title)
    for key, game_id in lookup.items():
        if key in normalized:
            return game_id
    return None


def _normalize(text: str) -> str:
    """Lowercase, remove accents, keep only alphanumeric and spaces."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]", " ", ascii_text.lower()).strip()


def _build_url(endpoint: str, params: dict[str, object]) -> str:
    return f"{_YOUTUBE_API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"


def _api_get(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None
