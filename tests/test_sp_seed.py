from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import csv


def read_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows


def test_sp_seed_camplink(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "sp_seed.py"
    out_dir = tmp_path / "seeds"
    cmd = [
        sys.executable,
        str(script),
        "--tables",
        "profile,campaign_history,campaign_level_report",
        "--mode",
        "reset",
        "--num-per-parent",
        "2",
        "--report-days",
        "3",
        "--catalog",
        str(repo_root / "docs" / "catalog_slim.json"),
        "--out-dir",
        str(out_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    # Validate files exist
    ch = out_dir / "campaign_history_data.csv"
    clr = out_dir / "campaign_level_report_data.csv"
    assert ch.exists() and clr.exists()

    ch_header, ch_rows = read_csv(ch)
    clr_header, clr_rows = read_csv(clr)
    # Basic invariants
    assert "id" in ch_header or "campaign_id" in ch_header
    assert "date" in clr_header or "date_day" in clr_header
    # Row counts
    assert len(ch_rows) == 2
    assert len(clr_rows) == 2 * 3


