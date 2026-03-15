"""TikTok reference channel connector — uses DuckDuckGo HTML search (no API key needed).

For each TikTok creator, searches for their recent game content and matches
against the games seed. Since TikTok has no public API, this is a best-effort
approach: it searches the web for what each creator is covering.
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}
_REQUEST_DELAY = 2.0  # seconds between requests (be polite)


def collect_tiktok_reference_metrics(
    channels: Sequence[str],
    games: Sequence[GameSeed],
    collected_at: datetime,
    request_delay: float = _REQUEST_DELAY,
) -> list[CollectedMetric]:
    """Search DuckDuckGo for each TikTok creator and count which games they cover."""
    if not channels:
        return []

    game_coverage: dict[str, int] = {game.game_id: 0 for game in games}
    game_lookup = _build_game_lookup(games)
    channels_ok = 0

    for i, channel in enumerate(channels):
        if i > 0:
            time.sleep(request_delay)

        handle = channel.strip().lstrip("@")
        try:
            text = _fetch_channel_content(handle)
            if not text:
                print(f"  [tiktok_search] @{handle}: sem resultados")
                continue

            matched: set[str] = set()
            for key, game_id in game_lookup.items():
                if key in _normalize(text):
                    matched.add(game_id)

            for game_id in matched:
                game_coverage[game_id] += 1

            channels_ok += 1
            found = [g for g in games if g.game_id in matched]
            names = ", ".join(g.name for g in found) if found else "nenhum"
            print(f"  [tiktok_search] @{handle}: jogos encontrados -> {names}")

        except Exception as exc:
            print(f"  [tiktok_search] Erro ao buscar @{handle}: {exc}")

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


def _fetch_channel_content(handle: str) -> str:
    """Query DuckDuckGo for what games a TikTok creator is covering."""
    query = f"tiktok @{handle} gameplay"
    params = urllib.parse.urlencode({"q": query, "kl": "br-pt"})
    url = f"{_DDG_URL}?{params}"

    req = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        return ""

    # Strip HTML tags and decode entities
    text = re.sub(r"<[^>]+>", " ", body)
    return html_lib.unescape(text)


def _build_game_lookup(games: Sequence[GameSeed]) -> dict[str, str]:
    """Map normalized name variants → game_id."""
    lookup: dict[str, str] = {}
    for game in games:
        _add(lookup, _normalize(game.name), game.game_id)
        for query in game.youtube_queries:
            _add(lookup, _normalize(query), game.game_id)
        first_word = game.name.split()[0]
        if len(first_word) >= 4:
            _add(lookup, _normalize(first_word), game.game_id)
    return lookup


def _add(lookup: dict[str, str], key: str, value: str) -> None:
    if key and key not in lookup:
        lookup[key] = value


def _normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]", " ", ascii_text.lower()).strip()
