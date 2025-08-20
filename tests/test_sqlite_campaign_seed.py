from __future__ import annotations

import csv
import os
import sqlite3
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sqlite_campaign_seed.py"


def run_generator(db_path: Path, out_dir: Path, mode: str, num_campaigns: int, report_days: int) -> None:
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        "--db",
        str(db_path),
        "--out-dir",
        str(out_dir),
        "--mode",
        mode,
        "--num-campaigns",
        str(num_campaigns),
        "--report-days",
        str(report_days),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(f"generator failed: rc={proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows


def test_reset_creates_ids_from_one_and_writes_csvs(tmp_path: Path):
    db_path = tmp_path / "amazon_ads.sqlite"
    out_dir = tmp_path / "seeds"

    run_generator(db_path, out_dir, mode="reset", num_campaigns=3, report_days=3)

    # Validate DB rows and auto-increment ids
    conn = sqlite3.connect(str(db_path))
    try:
        rows = list(conn.execute("SELECT id FROM campaigns ORDER BY id"))
        ids = [r[0] for r in rows]
        assert ids == [1, 2, 3]
    finally:
        conn.close()

    # Validate campaign_history_data.csv
    ch_path = out_dir / "campaign_history_data.csv"
    assert ch_path.exists()
    ch_header, ch_rows = read_csv(ch_path)
    expected_ch_columns = {
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
    }
    assert set(ch_header) >= expected_ch_columns
    assert len(ch_rows) == 3
    assert sorted(int(r["id"]) for r in ch_rows) == [1, 2, 3]

    # Validate campaign_level_report_data.csv
    clr_path = out_dir / "campaign_level_report_data.csv"
    assert clr_path.exists()
    clr_header, clr_rows = read_csv(clr_path)
    expected_clr_columns = {
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
    }
    assert set(clr_header) >= expected_clr_columns
    # 3 campaigns * 3 days
    assert len(clr_rows) == 9

    # Metric invariants and date window
    today = date.today()
    earliest = today - timedelta(days=3 - 1)
    for r in clr_rows:
        d = date.fromisoformat(r["date"])
        assert earliest <= d <= today
        clicks = int(r["clicks"]) if r.get("clicks") else 0
        impressions = int(r["impressions"]) if r.get("impressions") else 0
        cost = float(r["cost"]) if r.get("cost") else 0.0
        assert impressions >= clicks >= 0
        assert cost >= 0


def test_append_continues_autoincrement_and_updates_csvs(tmp_path: Path):
    db_path = tmp_path / "amazon_ads.sqlite"
    out_dir = tmp_path / "seeds"

    # First reset to 2 campaigns
    run_generator(db_path, out_dir, mode="reset", num_campaigns=2, report_days=2)
    # Then append 3 more
    run_generator(db_path, out_dir, mode="append", num_campaigns=3, report_days=2)

    # DB now should have 5 campaigns with ids 1..5
    conn = sqlite3.connect(str(db_path))
    try:
        rows = list(conn.execute("SELECT id FROM campaigns ORDER BY id"))
        ids = [r[0] for r in rows]
        assert ids == [1, 2, 3, 4, 5]
    finally:
        conn.close()

    # campaign_history_data.csv should have 5 rows
    ch_path = out_dir / "campaign_history_data.csv"
    _, ch_rows = read_csv(ch_path)
    assert len(ch_rows) == 5
    assert sorted(int(r["id"]) for r in ch_rows) == [1, 2, 3, 4, 5]

    # campaign_level_report_data.csv should have 5 * 2 rows
    clr_path = out_dir / "campaign_level_report_data.csv"
    _, clr_rows = read_csv(clr_path)
    assert len(clr_rows) == 10


