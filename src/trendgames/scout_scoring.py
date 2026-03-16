"""Game Scout scoring: formula optimized for short-form vertical content creators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from trendgames.domain import ChannelProfile, GameSeed


@dataclass(frozen=True)
class ScoutScore:
    game_id: str
    game_name: str
    score_total: float  # 0-10
    score_viral: float
    score_curiosidade: float
    score_funil: float
    score_producao: float
    tiktok_pct: int
    shorts_pct: int
    reels_pct: int
    urgencia: str
    coverage_count: int
    covered_by: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tag sets that influence each scoring dimension
# ---------------------------------------------------------------------------

_VIRAL_TAGS = {"puzzle", "horror", "wtf", "bizarro", "satisfying", "escape", "frustrante"}
_CURIOSIDADE_TAGS = {"curioso", "wtf", "bizarro", "misterio", "escape", "puzzle", "horror"}
_FUNIL_TAGS = {"indie", "narrativa", "deep", "roguelite", "cartas", "misterio", "horror", "puzzle"}
_PRODUCAO_EASY_TAGS = {"casual", "puzzle", "satisfying", "indie", "cartas", "sandbox", "criacao"}
_PRODUCAO_HARD_TAGS = {"shooter", "moba", "competitivo", "acao", "construcao", "destruicao"}

_TIKTOK_TAGS = {"wtf", "bizarro", "horror", "puzzle", "frustrante", "escape"}
_SHORTS_TAGS = {"satisfying", "puzzle", "casual", "curioso", "indie", "cartas"}
_REELS_TAGS = {"satisfying", "curioso", "casual", "indie", "puzzle", "criacao"}


def calculate_scout_scores(
    games: Sequence[GameSeed],
    metrics: list[dict[str, object]],
    profile: ChannelProfile,
    top_n: int = 10,
) -> list[ScoutScore]:
    """Calculate scout scores for all games and return top N sorted by score."""

    coverage_map = _build_coverage_map(metrics)

    scores: list[ScoutScore] = []
    for game in games:
        tags_lower = [t.lower() for t in game.tags]
        tag_set = set(tags_lower)

        coverage_count = coverage_map.get(game.game_id, {}).get("count", 0)
        covered_by = coverage_map.get(game.game_id, {}).get("channels", [])

        viral = _score_from_tags(tag_set, _VIRAL_TAGS, base=3.0, per_tag=1.4)
        viral = _boost_by_coverage(viral, coverage_count, boost_per=1.5)

        curiosidade = _score_from_tags(tag_set, _CURIOSIDADE_TAGS, base=2.5, per_tag=1.5)

        funil = _score_from_tags(tag_set, _FUNIL_TAGS, base=2.0, per_tag=1.3)

        producao = _producao_score(tag_set)

        total = (
            viral * 0.40
            + curiosidade * 0.25
            + funil * 0.20
            + producao * 0.15
        )
        total = round(min(10.0, max(0.0, total)), 1)

        urgencia = _determine_urgencia(coverage_count, total)

        tiktok_pct = _platform_pct(tag_set, _TIKTOK_TAGS, base=50)
        shorts_pct = _platform_pct(tag_set, _SHORTS_TAGS, base=50)
        reels_pct = _platform_pct(tag_set, _REELS_TAGS, base=45)

        scores.append(ScoutScore(
            game_id=game.game_id,
            game_name=game.name,
            score_total=total,
            score_viral=round(min(10.0, viral), 1),
            score_curiosidade=round(min(10.0, curiosidade), 1),
            score_funil=round(min(10.0, funil), 1),
            score_producao=round(min(10.0, producao), 1),
            tiktok_pct=tiktok_pct,
            shorts_pct=shorts_pct,
            reels_pct=reels_pct,
            urgencia=urgencia,
            coverage_count=coverage_count,
            covered_by=covered_by,
            tags=tags_lower,
        ))

    scores.sort(key=lambda s: s.score_total, reverse=True)
    return scores[:top_n]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_REFERENCE_PLATFORMS = {"reference_channels", "reference_channels_youtube", "reference_channels_tiktok"}


def _build_coverage_map(metrics: list[dict[str, object]]) -> dict[str, dict[str, Any]]:
    """Aggregate coverage_count across all reference channel platforms (YouTube)."""
    result: dict[str, dict[str, Any]] = {}
    for row in metrics:
        if str(row.get("platform")) not in _REFERENCE_PLATFORMS:
            continue
        if str(row.get("metric_type")) != "coverage_count":
            continue
        game_id = str(row["game_id"])
        count = int(float(row.get("value", 0)))
        entry = result.setdefault(game_id, {"count": 0, "channels": []})
        entry["count"] += count
    return result



def _score_from_tags(
    tag_set: set[str],
    relevant_tags: set[str],
    base: float,
    per_tag: float,
) -> float:
    """Calculate a 0-10 score based on tag overlap."""
    matches = len(tag_set & relevant_tags)
    return min(10.0, base + matches * per_tag)


def _boost_by_coverage(score: float, coverage_count: int, boost_per: float) -> float:
    """Increase score based on how many reference channels covered the game."""
    return min(10.0, score + coverage_count * boost_per)


def _producao_score(tag_set: set[str]) -> float:
    """Production ease: high for simple games, low for complex ones."""
    easy = len(tag_set & _PRODUCAO_EASY_TAGS)
    hard = len(tag_set & _PRODUCAO_HARD_TAGS)
    score = 5.0 + easy * 1.2 - hard * 1.8
    return max(1.0, min(10.0, score))


def _determine_urgencia(coverage_count: int, score_total: float) -> str:
    if coverage_count >= 2:
        return "GRAVAR AGORA"
    if coverage_count == 1:
        return "GRAVAR ESSA SEMANA"
    if score_total >= 7.0:
        return "PODE PLANEJAR"
    return "FICAR DE OLHO"


def _platform_pct(tag_set: set[str], relevant_tags: set[str], base: int) -> int:
    """Estimate platform fit percentage (40-95%) based on tag overlap."""
    matches = len(tag_set & relevant_tags)
    pct = base + matches * 10
    return max(40, min(95, pct))


def _generate_hashtags(game_name: str, tags: list[str]) -> str:
    """Generate relevant hashtags for the game."""
    clean_name = game_name.replace(" ", "").replace("'", "")
    hashtags = [f"#{clean_name}"]

    tag_hashtag_map = {
        "horror": "#HorrorGames",
        "indie": "#IndieGames",
        "puzzle": "#PuzzleGames",
        "bizarro": "#JogosBizarros",
        "wtf": "#WTF",
        "satisfying": "#Satisfying",
        "curioso": "#GamesInteressantes",
        "casual": "#CasualGames",
        "cooperativo": "#CoopGames",
        "roguelite": "#Roguelite",
        "cartas": "#CardGames",
        "escape": "#EscapeGames",
    }

    for tag in tags:
        if tag in tag_hashtag_map:
            hashtags.append(tag_hashtag_map[tag])

    hashtags.append("#GameplayShorts")
    return " ".join(hashtags[:6])


def _generate_reason(tags: list[str], coverage_count: int) -> str:
    """Generate a short 'why it works' explanation."""
    parts: list[str] = []

    tag_set = set(tags)
    if tag_set & {"horror", "wtf", "bizarro"}:
        parts.append("Horror/bizarro com mecanica WTF = para de scrollar.")
    elif tag_set & {"puzzle", "satisfying"}:
        parts.append("Visual satisfying + puzzle = retencao alta.")
    elif tag_set & {"curioso"}:
        parts.append("Fator curiosidade gera cliques organicos.")

    if tag_set & {"indie", "roguelite", "cartas", "horror"}:
        parts.append("Funil: gameplay completo rende video longo.")
    elif tag_set & {"casual", "sandbox"}:
        parts.append("Formato casual permite serie de shorts.")

    if coverage_count >= 2:
        parts.append(f"Trend confirmado: {coverage_count} canais ja cobriram.")
    elif coverage_count == 1:
        parts.append("1 canal de referencia cobriu recentemente.")

    return " ".join(parts) if parts else "Jogo com potencial para conteudo vertical."


def format_scout_report(
    scores: list[ScoutScore],
    profile: ChannelProfile,
    channels_checked: int,
) -> str:
    """Format the full scout report as a string for CLI output."""
    lines: list[str] = []
    date_str = _today_str()

    # Header
    lines.append("")
    lines.append("=" * 56)
    lines.append(f"  RELATORIO GAME SCOUT -- {profile.channel_name}")
    lines.append(f"  Data: {date_str}  |  Canais checados: {channels_checked}")
    lines.append("=" * 56)

    # Channels checked
    lines.append("")
    lines.append("CANAIS CHECADOS:")
    if profile.reference_channels_tiktok:
        lines.append("  TikTok:")
        for ch in profile.reference_channels_tiktok:
            lines.append(f"    * {ch}")
    if profile.reference_channels_youtube:
        lines.append("  YouTube:")
        for ch in profile.reference_channels_youtube:
            lines.append(f"    * {ch}")

    # Table header
    lines.append("")
    lines.append("TOP JOGOS -- Rankeados por Score Game Scout")
    sep = "-" * 78
    lines.append(sep)
    lines.append(
        f" {'#':>2} | {'Jogo':<23} | {'Cob.':>4} | {'TikTok':>6} | {'Shorts':>6} | {'Reels':>5} | {'Score':>5} | Urgencia"
    )
    lines.append(sep)

    for rank, s in enumerate(scores, start=1):
        lines.append(
            f" {rank:>2} | {s.game_name:<23} | {s.coverage_count:>4} | {s.tiktok_pct:>5}% | {s.shorts_pct:>5}% | {s.reels_pct:>4}% | {s.score_total:>5} | {s.urgencia}"
        )

    # Detailed analysis
    lines.append("")
    lines.append("ANALISE DETALHADA:")
    lines.append("-" * 40)

    for rank, s in enumerate(scores, start=1):
        lines.append(f"{rank}. {s.game_name}  [Score: {s.score_total} | {s.urgencia}]")
        lines.append(f"   Tags: {', '.join(s.tags)}")
        if s.covered_by:
            lines.append(f"   Cobertura: {', '.join(s.covered_by)}")
        elif s.coverage_count > 0:
            lines.append(f"   Cobertura: {s.coverage_count} canal(is)")
        lines.append(
            f"   Viral: {s.score_viral}  Curiosidade: {s.score_curiosidade}  "
            f"Funil: {s.score_funil}  Producao: {s.score_producao}"
        )
        reason = _generate_reason(s.tags, s.coverage_count)
        lines.append(f"   Por que funciona: {reason}")
        hashtags = _generate_hashtags(s.game_name, s.tags)
        lines.append(f"   Hashtags: {hashtags}")
        lines.append("")

    return "\n".join(lines)


def _today_str() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
