from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Iterable

from trendgames.domain import GameSeed, PlatformMetric, TrendScore


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            tags_json TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ok',
            notes TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS platform_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            game_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL DEFAULT '',
            raw_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id) ON DELETE CASCADE,
            FOREIGN KEY(game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            UNIQUE(snapshot_id, game_id, platform, metric_type)
        );

        CREATE TABLE IF NOT EXISTS trend_scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            game_id TEXT NOT NULL,
            score_total REAL NOT NULL,
            score_popularity REAL NOT NULL,
            score_growth REAL NOT NULL,
            score_multiplatform REAL NOT NULL,
            score_fit REAL NOT NULL,
            explanation_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id) ON DELETE CASCADE,
            FOREIGN KEY(game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            UNIQUE(snapshot_id, game_id)
        );

        CREATE INDEX IF NOT EXISTS idx_platform_metrics_snapshot
            ON platform_metrics(snapshot_id);
        CREATE INDEX IF NOT EXISTS idx_platform_metrics_game
            ON platform_metrics(game_id);
        CREATE INDEX IF NOT EXISTS idx_platform_metrics_snapshot_platform_type
            ON platform_metrics(snapshot_id, platform, metric_type);
        CREATE INDEX IF NOT EXISTS idx_trend_scores_snapshot
            ON trend_scores(snapshot_id);
        """
    )
    connection.commit()


def upsert_games(connection: sqlite3.Connection, games: Iterable[GameSeed]) -> None:
    payload = [(game.game_id, game.name, json.dumps(game.tags, ensure_ascii=True)) for game in games]
    connection.executemany(
        """
        INSERT INTO games (game_id, name, tags_json)
        VALUES (?, ?, ?)
        ON CONFLICT(game_id)
        DO UPDATE SET
            name = excluded.name,
            tags_json = excluded.tags_json
        """,
        payload,
    )
    connection.commit()


def create_snapshot(
    connection: sqlite3.Connection,
    status: str = "ok",
    notes: str = "",
    collected_at: datetime | None = None,
) -> int:
    timestamp = (collected_at or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    cursor = connection.execute(
        """
        INSERT INTO snapshots (collected_at, status, notes)
        VALUES (?, ?, ?)
        """,
        (timestamp, status, notes),
    )
    connection.commit()
    return int(cursor.lastrowid)


def insert_metrics(connection: sqlite3.Connection, metrics: Iterable[PlatformMetric]) -> int:
    payload = [
        (
            metric.snapshot_id,
            metric.game_id,
            metric.platform,
            metric.metric_type,
            metric.value,
            metric.unit,
            json.dumps(metric.raw, ensure_ascii=True),
        )
        for metric in metrics
    ]
    if not payload:
        return 0

    connection.executemany(
        """
        INSERT INTO platform_metrics (
            snapshot_id, game_id, platform, metric_type, value, unit, raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_id, game_id, platform, metric_type)
        DO UPDATE SET
            value = excluded.value,
            unit = excluded.unit,
            raw_json = excluded.raw_json
        """,
        payload,
    )
    connection.commit()
    return len(payload)


def replace_scores(connection: sqlite3.Connection, scores: Iterable[TrendScore]) -> int:
    payload = [
        (
            score.snapshot_id,
            score.game_id,
            score.score_total,
            score.score_popularity,
            score.score_growth,
            score.score_multiplatform,
            score.score_fit,
            json.dumps(score.explanation, ensure_ascii=True),
        )
        for score in scores
    ]
    if not payload:
        return 0

    connection.executemany(
        """
        INSERT INTO trend_scores (
            snapshot_id, game_id, score_total, score_popularity, score_growth,
            score_multiplatform, score_fit, explanation_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_id, game_id)
        DO UPDATE SET
            score_total = excluded.score_total,
            score_popularity = excluded.score_popularity,
            score_growth = excluded.score_growth,
            score_multiplatform = excluded.score_multiplatform,
            score_fit = excluded.score_fit,
            explanation_json = excluded.explanation_json
        """,
        payload,
    )
    connection.commit()
    return len(payload)


def get_latest_snapshot_id(connection: sqlite3.Connection) -> int | None:
    row = connection.execute(
        "SELECT snapshot_id FROM snapshots ORDER BY snapshot_id DESC LIMIT 1"
    ).fetchone()
    return int(row["snapshot_id"]) if row else None


def get_previous_snapshot_id(connection: sqlite3.Connection, snapshot_id: int) -> int | None:
    row = connection.execute(
        """
        SELECT snapshot_id
        FROM snapshots
        WHERE snapshot_id < ?
        ORDER BY snapshot_id DESC
        LIMIT 1
        """,
        (snapshot_id,),
    ).fetchone()
    return int(row["snapshot_id"]) if row else None


def get_snapshot_metrics(connection: sqlite3.Connection, snapshot_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT
            pm.snapshot_id,
            pm.game_id,
            g.name AS game_name,
            g.tags_json,
            pm.platform,
            pm.metric_type,
            pm.value,
            pm.unit,
            pm.raw_json
        FROM platform_metrics pm
        INNER JOIN games g ON g.game_id = pm.game_id
        WHERE pm.snapshot_id = ?
        ORDER BY g.name, pm.platform, pm.metric_type
        """,
        (snapshot_id,),
    ).fetchall()

    parsed: list[dict[str, object]] = []
    for row in rows:
        parsed.append(
            {
                "snapshot_id": row["snapshot_id"],
                "game_id": row["game_id"],
                "game_name": row["game_name"],
                "tags": _safe_json_loads(row["tags_json"], default=[]),
                "platform": row["platform"],
                "metric_type": row["metric_type"],
                "value": row["value"],
                "unit": row["unit"],
                "raw": _safe_json_loads(row["raw_json"], default={}),
            }
        )
    return parsed


def get_scores(connection: sqlite3.Connection, snapshot_id: int, limit: int = 10) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT
            ts.snapshot_id,
            ts.game_id,
            g.name AS game_name,
            ts.score_total,
            ts.score_popularity,
            ts.score_growth,
            ts.score_multiplatform,
            ts.score_fit,
            ts.explanation_json
        FROM trend_scores ts
        INNER JOIN games g ON g.game_id = ts.game_id
        WHERE ts.snapshot_id = ?
        ORDER BY ts.score_total DESC, g.name ASC
        LIMIT ?
        """,
        (snapshot_id, limit),
    ).fetchall()

    result: list[dict[str, object]] = []
    for row in rows:
        result.append(
            {
                "snapshot_id": row["snapshot_id"],
                "game_id": row["game_id"],
                "game_name": row["game_name"],
                "score_total": row["score_total"],
                "score_popularity": row["score_popularity"],
                "score_growth": row["score_growth"],
                "score_multiplatform": row["score_multiplatform"],
                "score_fit": row["score_fit"],
                "explanation": _safe_json_loads(row["explanation_json"], default={}),
            }
        )
    return result


def has_scores(connection: sqlite3.Connection, snapshot_id: int) -> bool:
    row = connection.execute(
        "SELECT 1 FROM trend_scores WHERE snapshot_id = ? LIMIT 1",
        (snapshot_id,),
    ).fetchone()
    return row is not None


def _safe_json_loads(raw: object, default: object) -> object:
    if not isinstance(raw, str):
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default
