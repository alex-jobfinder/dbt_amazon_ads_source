from __future__ import annotations

import argparse
import csv
import os
import random
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .seed_core import connect as core_connect, ensure_table, reset_table, write_csv, utc_ts, daterange

@dataclass
class Config:
    db_path: Path
    mode: str  # "append" | "reset"
    num_campaigns: int
    report_days: int
    out_dir: Path


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS campaigns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    profile_id      TEXT,
    portfolio_id    TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
"""


def reset_schema(conn: sqlite3.Connection) -> None:
    reset_table(conn, "campaigns", CREATE_TABLE_SQL)


def add_campaigns(conn: sqlite3.Connection, n: int) -> None:
    if n <= 0:
        return
    campaigns: List[Tuple[str, str, str, str, str]] = []
    for _ in range(n):
        name = f"Campaign {random.randint(100000, 999999)}"
        profile_id = str(random.randint(10, 99))
        portfolio_id = str(random.randint(1000, 9999)) if random.random() < 0.7 else None
        created = utc_ts()
        updated = utc_ts()
        campaigns.append((name, profile_id, portfolio_id, created, updated))
    conn.executemany(
        "INSERT INTO campaigns(name, profile_id, portfolio_id, created_at, updated_at) VALUES(?,?,?,?,?)",
        campaigns,
    )
    conn.commit()


def fetch_campaigns(conn: sqlite3.Connection) -> List[Tuple[int, str, Optional[str], Optional[str], str, str]]:
    cur = conn.execute(
        "SELECT id, name, profile_id, portfolio_id, created_at, updated_at FROM campaigns ORDER BY id ASC"
    )
    return list(cur.fetchall())


def ensure_schema(conn: sqlite3.Connection) -> None:
    ensure_table(conn, CREATE_TABLE_SQL)


def export_campaign_history(out_path: Path, rows: List[Tuple[int, str, Optional[str], Optional[str], str, str]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "id",
        "last_updated_date",
        "_fivetran_synced",
        "bidding_strategy",
        "creation_date",
        "budget",
        "end_date",
        "name",
        "portfolio_id",
        "profile_id",
        "serving_status",
        "start_date",
        "state",
        "targeting_type",
        "budget_type",
        "effective_budget",
    ]

    def row_to_dict(r: Tuple[int, str, Optional[str], Optional[str], str, str]) -> dict:
        cid, name, profile_id, portfolio_id, created_at, updated_at = r
        start_dt = (date.today() - timedelta(days=random.randint(30, 120))).strftime("%Y-%m-%d")
        return {
            "id": cid,
            "last_updated_date": updated_at,
            "_fivetran_synced": utc_ts(),
            "bidding_strategy": random.choice(["autoForSales", "manual", "legacyForSales"]),
            "creation_date": created_at,
            "budget": f"{random.uniform(100, 5000):.2f}",
            "end_date": "",
            "name": name,
            "portfolio_id": portfolio_id or "",
            "profile_id": profile_id or "",
            "serving_status": random.choice(["CAMPAIGN_STATUS_ENABLED", "CAMPAIGN_PAUSED"]),
            "start_date": start_dt,
            "state": random.choice(["enabled", "paused", "archived"]),
            "targeting_type": random.choice(["manual", "auto"]),
            "budget_type": random.choice(["daily", "lifetime"]),
            "effective_budget": "",
        }

    write_csv(out_path, header, (row_to_dict(r) for r in rows))


def export_campaign_level_report(
    out_path: Path,
    rows: List[Tuple[int, str, Optional[str], Optional[str], str, str]],
    days: int,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "campaign_id",
        "date",
        "_fivetran_synced",
        "campaign_applicable_budget_rule_id",
        "campaign_applicable_budget_rule_name",
        "campaign_bidding_strategy",
        "campaign_budget_amount",
        "campaign_budget_currency_code",
        "campaign_budget_type",
        "clicks",
        "cost",
        "impressions",
        "campaign_rule_based_budget_amount",
        "sales_7_d",
        "purchases_30_d",
        "sales_30_d",
    ]

    def metrics() -> Tuple[int, int, float, int, float]:
        clicks = max(0, int(random.gauss(3, 5)))
        impressions = max(clicks, clicks + int(abs(random.gauss(20, 50))))
        cpc = random.uniform(0.3, 1.5)
        cost = round(clicks * cpc, 2)
        purchases = max(0, min(clicks, int(random.gauss(1, 2))))
        sales = round(purchases * random.uniform(10, 100), 2)
        return clicks, impressions, cost, purchases, sales

    def iter_rows():
        for cid, *_ in rows:
            for d in daterange(days):
                clicks, impressions, cost, purchases, sales = metrics()
                yield {
                    "campaign_id": cid,
                    "date": d.strftime("%Y-%m-%d"),
                    "_fivetran_synced": utc_ts(),
                    "campaign_applicable_budget_rule_id": "",
                    "campaign_applicable_budget_rule_name": "",
                    "campaign_bidding_strategy": random.choice(["optimizeForSales", "autoForSales", "manual"]),
                    "campaign_budget_amount": random.uniform(100, 5000),
                    "campaign_budget_currency_code": "USD",
                    "campaign_budget_type": random.choice(["DAILY_BUDGET", "LIFETIME_BUDGET"]),
                    "clicks": clicks,
                    "cost": cost,
                    "impressions": impressions,
                    "campaign_rule_based_budget_amount": "",
                    "sales_7_d": random.randint(0, 25),
                    "purchases_30_d": purchases,
                    "sales_30_d": sales,
                }

    write_csv(out_path, header, iter_rows())


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="SQLite-backed campaign seed generator")
    parser.add_argument("--db", type=str, default="local/amazon_ads.sqlite", help="SQLite database path")
    parser.add_argument("--mode", type=str, choices=["append", "reset"], default="append", help="Append or reset database before generating")
    parser.add_argument("--num-campaigns", type=int, default=5, help="Number of campaigns to add when appending or after reset")
    parser.add_argument("--report-days", type=int, default=14, help="Number of days for campaign_level_report rows")
    parser.add_argument(
        "--out-dir",
        type=str,
        default="integration_tests/seeds",
        help="Directory for writing *_data.csv seeds",
    )
    args = parser.parse_args()
    return Config(
        db_path=Path(args.db),
        mode=args.mode,
        num_campaigns=args.num_campaigns,
        report_days=args.report_days,
        out_dir=Path(args.out_dir),
    )


def main() -> None:
    cfg = parse_args()
    conn = core_connect(cfg.db_path)
    try:
        if cfg.mode == "reset":
            reset_schema(conn)
            add_campaigns(conn, cfg.num_campaigns)
        else:
            ensure_schema(conn)
            add_campaigns(conn, cfg.num_campaigns)

        rows = fetch_campaigns(conn)

        ch_path = cfg.out_dir / "campaign_history_data.csv"
        clr_path = cfg.out_dir / "campaign_level_report_data.csv"

        export_campaign_history(ch_path, rows)
        export_campaign_level_report(clr_path, rows, cfg.report_days)

        print(f"Wrote: {ch_path}")
        print(f"Wrote: {clr_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


