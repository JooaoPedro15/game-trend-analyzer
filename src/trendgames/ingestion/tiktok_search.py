"""TikTok connector — limitação: sem API pública do TikTok.

TikTok não oferece API pública para dados de criadores ou vídeos.
Scraping de motores de busca (DDG, Google) é bloqueado por CAPTCHA.

O que este módulo faz:
- Informa ao usuário que cobertura real de criadores TikTok requer TikTok API
- Retorna métricas vazias (o scout_scoring.py usa heurística por tags como fallback)

Para cobertura real dos canais de referência do TikTok (@lohzao, @cofflei, etc.),
seria necessário: TikTok Research API (aprovação manual) ou TikTok for Business API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from trendgames.domain import GameSeed
from trendgames.ingestion import CollectedMetric


def collect_tiktok_reference_metrics(
    channels: Sequence[str],
    games: Sequence[GameSeed],
    collected_at: datetime,
) -> list[CollectedMetric]:
    """Informa a limitação e retorna vazio — virality TikTok é estimada por tags."""
    if channels:
        handles = ", ".join(c.strip().lstrip("@") for c in channels)
        print(f"  [tiktok] Canais: {handles}")
        print(f"  [tiktok] Cobertura de criadores requer TikTok API (nao disponivel)")
        print(f"  [tiktok] Virality TikTok sera estimada por tags dos jogos")
    return []
