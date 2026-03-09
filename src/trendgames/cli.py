from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys

from trendgames.domain import PlatformMetric
from trendgames.ingestion.csv_import import import_csv_metrics
from trendgames.ingestion.steam import collect_steam_metrics
from trendgames.ingestion.twitch import collect_twitch_metrics
from trendgames.ingestion.youtube import collect_youtube_metrics
from trendgames.scoring import calculate_scores
from trendgames.settings import (
    DEFAULT_CHANNEL_PROFILE_PATH,
    DEFAULT_DB_PATH,
    DEFAULT_GAMES_SEED_PATH,
    load_channel_profile,
    load_games_seed,
)
from trendgames.storage import (
    connect,
    create_snapshot,
    get_latest_snapshot_id,
    get_previous_snapshot_id,
    get_scores,
    get_snapshot_metrics,
    has_scores,
    init_db,
    insert_metrics,
    replace_scores,
    upsert_games,
)


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        raise SystemExit(_command_ingest(args))
    if args.command == "score":
        raise SystemExit(_command_score(args))
    if args.command == "recommend":
        raise SystemExit(_command_recommend(args))
    if args.command == "run":
        raise SystemExit(_command_run(args))

    parser.print_help()
    raise SystemExit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trendgames",
        description="TrendGames MVP local CLI (ingest -> score -> recommend).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Create one snapshot with platform metrics.")
    ingest_parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite path.")
    ingest_parser.add_argument("--seed", default=str(DEFAULT_GAMES_SEED_PATH), help="Games seed YAML.")
    ingest_parser.add_argument("--csv", default="", help="Optional CSV file with extra metrics.")

    score_parser = subparsers.add_parser("score", help="Calculate and persist score for one snapshot.")
    score_parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite path.")
    score_parser.add_argument("--profile", default=str(DEFAULT_CHANNEL_PROFILE_PATH), help="Channel profile YAML.")
    score_parser.add_argument("--snapshot-id", type=int, default=0, help="Snapshot id. Default is latest.")

    recommend_parser = subparsers.add_parser("recommend", help="Print top recommended games.")
    recommend_parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite path.")
    recommend_parser.add_argument("--profile", default=str(DEFAULT_CHANNEL_PROFILE_PATH), help="Channel profile YAML.")
    recommend_parser.add_argument("--snapshot-id", type=int, default=0, help="Snapshot id. Default is latest.")
    recommend_parser.add_argument("--top", type=int, default=10, help="How many games to show.")
    recommend_parser.add_argument(
        "--recompute",
        action="store_true",
        help="Force score recalculation before printing recommendations.",
    )

    run_parser = subparsers.add_parser("run", help="Run ingest + score + recommend in sequence.")
    run_parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite path.")
    run_parser.add_argument("--seed", default=str(DEFAULT_GAMES_SEED_PATH), help="Games seed YAML.")
    run_parser.add_argument("--profile", default=str(DEFAULT_CHANNEL_PROFILE_PATH), help="Channel profile YAML.")
    run_parser.add_argument("--csv", default="", help="Optional CSV file with extra metrics.")
    run_parser.add_argument("--top", type=int, default=10, help="How many games to show.")

    return parser


def _command_ingest(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    seed_path = Path(args.seed).resolve()
    csv_path = Path(args.csv).resolve() if args.csv else None

    games = load_games_seed(seed_path)
    collected_at = datetime.now(timezone.utc).replace(microsecond=0)

    with connect(db_path) as connection:
        init_db(connection)
        upsert_games(connection, games)
        snapshot_id = create_snapshot(connection, status="ok", notes="simulated ingestion", collected_at=collected_at)

        collected = []
        collected.extend(collect_twitch_metrics(games, collected_at))
        collected.extend(collect_youtube_metrics(games, collected_at))
        collected.extend(collect_steam_metrics(games, collected_at))
        if csv_path:
            collected.extend(import_csv_metrics(csv_path, games))

        metrics = [
            PlatformMetric(
                snapshot_id=snapshot_id,
                game_id=item.game_id,
                game_name=item.game_name,
                platform=item.platform,
                metric_type=item.metric_type,
                value=item.value,
                unit=item.unit,
                raw=item.raw,
            )
            for item in collected
        ]
        inserted = insert_metrics(connection, metrics)

    platform_counter = Counter(item.platform for item in collected)
    platform_breakdown = ", ".join(
        f"{platform}:{count}" for platform, count in sorted(platform_counter.items())
    )
    print(f"Snapshot {snapshot_id} created at {collected_at.isoformat()}")
    print(f"Games: {len(games)} | Metrics inserted: {inserted}")
    print(f"Platform metrics: {platform_breakdown or '-'}")
    return 0


def _command_score(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    profile_path = Path(args.profile).resolve()
    requested_snapshot_id = args.snapshot_id if args.snapshot_id > 0 else None

    with connect(db_path) as connection:
        init_db(connection)
        snapshot_id = requested_snapshot_id or get_latest_snapshot_id(connection)
        if snapshot_id is None:
            print("No snapshots found. Run `trendgames ingest` first.")
            return 1

        scored = _score_snapshot(connection, snapshot_id, profile_path)
        if scored == 0:
            print(f"Snapshot {snapshot_id} has no metrics to score.")
            return 1

        previous_id = get_previous_snapshot_id(connection, snapshot_id)

    previous_note = str(previous_id) if previous_id is not None else "none"
    print(f"Snapshot {snapshot_id} scored ({scored} games). Previous snapshot: {previous_note}.")
    return 0


def _command_recommend(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    profile_path = Path(args.profile).resolve()
    requested_snapshot_id = args.snapshot_id if args.snapshot_id > 0 else None
    top_n = max(1, int(args.top))

    with connect(db_path) as connection:
        init_db(connection)
        snapshot_id = requested_snapshot_id or get_latest_snapshot_id(connection)
        if snapshot_id is None:
            print("No snapshots found. Run `trendgames ingest` first.")
            return 1

        if args.recompute or not has_scores(connection, snapshot_id):
            scored = _score_snapshot(connection, snapshot_id, profile_path)
            if scored == 0:
                print(f"Snapshot {snapshot_id} has no metrics to score.")
                return 1

        rows = get_scores(connection, snapshot_id, limit=top_n)
        if not rows:
            print(f"No scores found for snapshot {snapshot_id}.")
            return 1

    _print_recommendations(snapshot_id, rows)
    return 0


def _command_run(args: argparse.Namespace) -> int:
    ingest_code = _command_ingest(args)
    if ingest_code != 0:
        return ingest_code

    db_path = Path(args.db).resolve()
    profile_path = Path(args.profile).resolve()
    top_n = max(1, int(args.top))
    with connect(db_path) as connection:
        init_db(connection)
        snapshot_id = get_latest_snapshot_id(connection)
        if snapshot_id is None:
            print("No snapshots found after ingestion.")
            return 1
        scored = _score_snapshot(connection, snapshot_id, profile_path)
        if scored == 0:
            print(f"Snapshot {snapshot_id} has no metrics to score.")
            return 1
        rows = get_scores(connection, snapshot_id, limit=top_n)
    _print_recommendations(snapshot_id, rows)
    return 0


def _score_snapshot(connection, snapshot_id: int, profile_path: Path) -> int:
    current_metrics = get_snapshot_metrics(connection, snapshot_id)
    if not current_metrics:
        return 0

    previous_id = get_previous_snapshot_id(connection, snapshot_id)
    previous_metrics = get_snapshot_metrics(connection, previous_id) if previous_id else []
    profile = load_channel_profile(profile_path)

    scores = calculate_scores(
        snapshot_id=snapshot_id,
        current_metrics=current_metrics,
        previous_metrics=previous_metrics,
        profile=profile,
    )
    replace_scores(connection, scores)
    return len(scores)


def _print_recommendations(snapshot_id: int, rows: list[dict[str, object]]) -> None:
    print(f"Recommendations for snapshot {snapshot_id}")
    for rank, row in enumerate(rows, start=1):
        explanation = row.get("explanation", {})
        strong_platforms = ""
        if isinstance(explanation, dict):
            strong = explanation.get("strong_platforms", [])
            if isinstance(strong, list):
                strong_platforms = ",".join(str(item) for item in strong)

        print(
            f"{rank:>2}. {row['score_total']:>6.2f} | {row['game_name']:<28} "
            f"| pop {row['score_popularity']:>5.1f} "
            f"grow {row['score_growth']:>5.1f} "
            f"multi {row['score_multiplatform']:>5.1f} "
            f"fit {row['score_fit']:>5.1f} "
            f"| strong: {strong_platforms or '-'}"
        )


if __name__ == "__main__":
    main(sys.argv[1:])
