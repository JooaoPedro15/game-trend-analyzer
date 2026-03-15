"""TikTok reference channel connector — DuckDuckGo targeted search (no API key).

Strategy: for each top-scoring game × each TikTok creator, search:
  "{creator_handle}" "{game_name}" tiktok
This checks if a specific creator has made TikTok content about a game.
Total queries = len(channels) × MAX_GAMES_TO_CHECK (default: 5 × 5 = 25).
"""

from __future__ import annotations

import html as html_lib
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric

_DDG_URL = "https://html.duckduckgo.com/html/"
_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}
_REQUEST_DELAY = 1.5  # seconds between DDG requests
_MAX_GAMES = 8        # only check the most tag-relevant games per channel

# Tags that indicate a game is likely to appear on TikTok gaming content
_VIRAL_TAG_WEIGHTS: dict[str, int] = {
    "wtf": 4, "horror": 3, "bizarro": 3, "puzzle": 2,
    "satisfying": 2, "curioso": 2, "escape": 2,
    "indie": 1, "cartas": 1, "roguelite": 1,
}


def collect_tiktok_reference_metrics(
    channels: Sequence[str],
    games: Sequence[GameSeed],
    collected_at: datetime,
    max_games: int = _MAX_GAMES,
    request_delay: float = _REQUEST_DELAY,
) -> list[CollectedMetric]:
    """For each TikTok creator, check which top games they appear to cover."""
    if not channels:
        return []

    top_games = _select_top_games(games, max_games)
    game_coverage: dict[str, int] = {game.game_id: 0 for game in games}
    channels_ok = 0
    request_count = 0

    for channel in channels:
        handle = channel.strip().lstrip("@")
        found_for_channel: list[str] = []

        for game in top_games:
            if request_count > 0:
                time.sleep(request_delay)
            request_count += 1

            if _creator_covers_game(handle, game.name):
                game_coverage[game.game_id] += 1
                found_for_channel.append(game.name)

        channels_ok += 1
        names = ", ".join(found_for_channel) if found_for_channel else "nenhum"
        print(f"  [tiktok_search] @{handle}: jogos encontrados -> {names}")

    if channels_ok == 0:
        return []

    return [
        CollectedMetric(
            game_id=game.game_id,
            game_name=game.name,
            platform="reference_channels_tiktok",
            metric_type="coverage_count",
            value=float(game_coverage.get(game.game_id, 0)),
            unit="mentions",
            raw={"source": "tiktok_search", "channels_analyzed": channels_ok},
        )
        for game in games
    ]


def _creator_covers_game(handle: str, game_name: str) -> bool:
    """Return True if DuckDuckGo finds evidence this TikTok creator covered the game."""
    query = f'"{handle}" "{game_name}" tiktok'
    params = urllib.parse.urlencode({"q": query, "kl": "br-pt"})
    url = f"{_DDG_URL}?{params}"

    req = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        return False

    # Strip tags, decode entities
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", body)).lower()

    # Positive signal: both the handle and game name appear in the results
    handle_norm = _normalize(handle)
    game_norm = _normalize(game_name)

    # Must find both handle and game name in the result text
    # Also require at least one "tiktok" reference to avoid false positives
    return (
        handle_norm in text
        and game_norm in text
        and "tiktok" in text
        and "no results" not in text
    )


def _select_top_games(games: Sequence[GameSeed], n: int) -> list[GameSeed]:
    """Return top N games ranked by viral tag weight (most likely to appear on TikTok)."""
    scored = [
        (sum(_VIRAL_TAG_WEIGHTS.get(t.lower(), 0) for t in g.tags), g)
        for g in games
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [g for _, g in scored[:n]]


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]", " ", ascii_text.lower()).strip()
