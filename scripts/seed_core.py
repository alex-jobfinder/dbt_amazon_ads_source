from __future__ import annotations

import csv
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
import json


# --- time helpers ---

def utc_ts(microseconds: bool = True) -> str:
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f" if microseconds else "%Y-%m-%d %H:%M:%S")


def daterange(days: int) -> Iterator[date]:
    end = date.today()
    start = end - timedelta(days=days - 1)
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


# --- sqlite helpers ---

def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def ensure_table(conn: sqlite3.Connection, create_table_sql: str) -> None:
    conn.execute(create_table_sql)
    conn.commit()


def reset_table(conn: sqlite3.Connection, table_name: str, create_table_sql: str) -> None:
    conn.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    ensure_table(conn, create_table_sql)


# --- csv helpers ---

def write_csv(path: Path, header: Sequence[str], rows: Iterable[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(header), extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: _serialize_value(r.get(k)) for k in header})


def _serialize_value(v: Optional[object]) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


# --- catalog helpers ---

def load_catalog_columns(
    catalog_path: Path,
    model_suffix: str,
) -> List[Tuple[str, str, int]]:
    """
    Return (name, type, index) for columns of the model whose unique_id endswith model_suffix
    or whose metadata.name equals model_suffix.
    """
    with catalog_path.open("r", encoding="utf-8") as f:
        catalog = json.load(f)
    nodes: Dict[str, dict] = catalog.get("nodes", {})
    selected: Optional[dict] = None
    for key, node in nodes.items():
        if key.endswith(model_suffix):
            selected = node
            break
        md = node.get("metadata", {})
        if str(md.get("name")) == model_suffix:
            selected = node
            break
    if not selected:
        return []
    cols = []
    for col_name, meta in (selected.get("columns", {}) or {}).items():
        name = meta.get("name", col_name)
        ctype = str(meta.get("type", "text"))
        try:
            cindex = int(meta.get("index", 10_000))
        except Exception:
            cindex = 10_000
        cols.append((name, ctype, cindex))
    cols.sort(key=lambda t: t[2])
    return cols


