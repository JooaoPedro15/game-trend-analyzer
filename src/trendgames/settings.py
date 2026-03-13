from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re
import unicodedata

_RE_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_RE_INT = re.compile(r"-?\d+")
_RE_FLOAT = re.compile(r"-?\d+\.\d+")
_RE_SLUG_STRIP = re.compile(r"[^a-zA-Z0-9]+")

from trendgames.domain import ChannelProfile, GameSeed

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "trendgames.db"
DEFAULT_CHANNEL_PROFILE_PATH = REPO_ROOT / "config" / "channel_profile.yaml"
DEFAULT_GAMES_SEED_PATH = REPO_ROOT / "config" / "games_seed.yaml"


DEFAULT_GAMES: list[GameSeed] = [
    GameSeed("fortnite", "Fortnite", ["battle-royale", "casual"]),
    GameSeed("minecraft", "Minecraft", ["sandbox", "survival"]),
    GameSeed("roblox", "Roblox", ["sandbox", "casual"]),
    GameSeed("valorant", "Valorant", ["fps", "competitive"]),
    GameSeed("counter-strike-2", "Counter-Strike 2", ["fps", "competitive"], steam_appid=730),
    GameSeed("league-of-legends", "League of Legends", ["moba", "competitive"]),
    GameSeed("ea-sports-fc-25", "EA Sports FC 25", ["sports", "competitive"]),
    GameSeed("gta-v", "Grand Theft Auto V", ["open-world", "sandbox"], steam_appid=271590),
    GameSeed("warzone", "Call of Duty: Warzone", ["fps", "battle-royale"]),
    GameSeed("helldivers-2", "Helldivers 2", ["co-op", "action"]),
    GameSeed("stardew-valley", "Stardew Valley", ["indie", "casual"], steam_appid=413150),
    GameSeed("palworld", "Palworld", ["indie", "sandbox"], steam_appid=1623730),
]

GAME_TAG_HINTS: dict[str, list[str]] = {
    "fortnite": ["battle-royale", "casual"],
    "valorant": ["fps", "competitive"],
    "counter-strike": ["fps", "competitive"],
    "minecraft": ["sandbox", "survival"],
    "roblox": ["sandbox", "casual"],
    "league": ["moba", "competitive"],
    "fifa": ["sports", "competitive"],
    "fc": ["sports", "competitive"],
    "call of duty": ["fps", "battle-royale"],
    "warzone": ["fps", "battle-royale"],
    "stardew": ["indie", "casual"],
    "palworld": ["indie", "sandbox"],
    "gta": ["open-world", "sandbox"],
    "grand theft auto": ["open-world", "sandbox"],
}


class SimpleYamlError(ValueError):
    pass


def load_games_seed(path: Path | None = None) -> list[GameSeed]:
    target = path or DEFAULT_GAMES_SEED_PATH
    if not target.exists():
        return DEFAULT_GAMES.copy()

    data = _load_simple_yaml_file(target)
    if not data:
        return DEFAULT_GAMES.copy()

    raw_games: list[object]
    if isinstance(data, dict) and isinstance(data.get("games"), list):
        raw_games = data["games"]
    elif isinstance(data, list):
        raw_games = data
    else:
        return DEFAULT_GAMES.copy()

    parsed: list[GameSeed] = []
    used_ids: set[str] = set()
    for item in raw_games:
        game = _coerce_game_seed(item)
        if game is None:
            continue
        unique_id = _unique_id(game.game_id, used_ids)
        parsed.append(replace(game, game_id=unique_id))
        used_ids.add(unique_id)

    if not parsed:
        return DEFAULT_GAMES.copy()
    return parsed


def load_channel_profile(path: Path | None = None) -> ChannelProfile:
    target = path or DEFAULT_CHANNEL_PROFILE_PATH
    if not target.exists():
        return ChannelProfile()

    data = _load_simple_yaml_file(target)
    if not isinstance(data, dict):
        return ChannelProfile()

    video_length = data.get("video_length_seconds", {})
    if not isinstance(video_length, dict):
        video_length = {}

    return ChannelProfile(
        channel_name=str(data.get("channel_name", "Canal")),
        content_type=_to_str_list(data.get("content_type")),
        platforms=_to_str_list(data.get("platforms")),
        preferred_game_types=_to_str_list(data.get("preferred_game_types")),
        avoided_game_types=_to_str_list(data.get("avoided_game_types")),
        video_length_min=_to_int(video_length.get("min")),
        video_length_max=_to_int(video_length.get("max")),
    )


def _coerce_game_seed(item: object) -> GameSeed | None:
    if isinstance(item, str):
        name = item.strip()
        if not name:
            return None
        game_id = _slugify(name)
        return GameSeed(game_id=game_id, name=name, tags=_infer_tags(name))

    if not isinstance(item, dict):
        return None

    name = str(item.get("name") or item.get("title") or item.get("game") or "").strip()
    if not name:
        return None

    game_id = _slugify(str(item.get("id", "")).strip() or name)
    tags = _to_str_list(item.get("tags")) or _infer_tags(name)
    queries = _to_str_list(item.get("youtube_queries"))
    steam_appid = _to_int(item.get("steam_appid"))

    return GameSeed(
        game_id=game_id,
        name=name,
        tags=tags,
        steam_appid=steam_appid,
        youtube_queries=queries,
    )


def _load_simple_yaml_file(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    try:
        return _parse_simple_yaml(text)
    except SimpleYamlError:
        return {}


def _parse_simple_yaml(text: str) -> object:
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        stripped = raw_line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        content = stripped.split(" #", 1)[0].rstrip()
        if not content:
            continue
        indent = len(raw_line) - len(stripped)
        lines.append((indent, content))

    if not lines:
        return {}

    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise SimpleYamlError("Could not parse full YAML content")
    return value


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[object, int]:
    _, content = lines[index]
    if content.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_dict(lines, index, indent)


def _parse_dict(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, object], int]:
    result: dict[str, object] = {}
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise SimpleYamlError(f"Unexpected indent for mapping: {content}")
        if content.startswith("- "):
            break
        if ":" not in content:
            raise SimpleYamlError(f"Invalid mapping line: {content}")

        key, tail = content.split(":", 1)
        key = key.strip()
        tail = tail.strip()
        index += 1

        if tail:
            result[key] = _parse_scalar(tail)
            continue

        if index < len(lines) and lines[index][0] > indent:
            child, index = _parse_block(lines, index, lines[index][0])
            result[key] = child
        else:
            result[key] = None
    return result, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[object], int]:
    result: list[object] = []
    while index < len(lines):
        line_indent, content = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise SimpleYamlError(f"Unexpected indent for list: {content}")
        if not content.startswith("- "):
            break

        item_text = content[2:].strip()
        index += 1

        if not item_text:
            if index < len(lines) and lines[index][0] > indent:
                child, index = _parse_block(lines, index, lines[index][0])
                result.append(child)
            else:
                result.append(None)
            continue

        # Minimal support for inline one-key dict item:
        # - name: Fortnite
        if ":" in item_text and not item_text.startswith(("'", '"')):
            key, tail = item_text.split(":", 1)
            key = key.strip()
            if _RE_IDENTIFIER.fullmatch(key):
                item_dict: dict[str, object] = {key: _parse_scalar(tail.strip()) if tail.strip() else None}
                if index < len(lines) and lines[index][0] > indent:
                    child, index = _parse_block(lines, index, lines[index][0])
                    if isinstance(child, dict):
                        item_dict.update(child)
                result.append(item_dict)
                continue

        result.append(_parse_scalar(item_text))
    return result, index


def _parse_scalar(value: str) -> object:
    stripped = value.strip()
    if stripped in {"null", "Null", "NULL", "~"}:
        return None
    if stripped in {"true", "True", "TRUE"}:
        return True
    if stripped in {"false", "False", "FALSE"}:
        return False
    if stripped.startswith(("'", '"')) and stripped.endswith(("'", '"')) and len(stripped) >= 2:
        return stripped[1:-1]
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    if _RE_INT.fullmatch(stripped):
        return int(stripped)
    if _RE_FLOAT.fullmatch(stripped):
        return float(stripped)
    return stripped


def _to_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [s for item in value if (s := str(item).strip())]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _unique_id(base: str, used: set[str]) -> str:
    if base not in used:
        return base
    suffix = 2
    while f"{base}-{suffix}" in used:
        suffix += 1
    return f"{base}-{suffix}"


def _infer_tags(name: str) -> list[str]:
    lower_name = name.lower()
    tags: list[str] = []
    for hint, hint_tags in GAME_TAG_HINTS.items():
        if hint in lower_name:
            tags.extend(hint_tags)
    return sorted(set(tags))


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = _RE_SLUG_STRIP.sub("-", normalized).strip("-").lower()
    return slug or "game"
