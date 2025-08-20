from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import List


def ensure_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def create_table(conn: sqlite3.Connection, table: str, headers: List[str]) -> None:
    cols = ", ".join([f'"{h}" TEXT' for h in headers])
    sql = f"CREATE TABLE IF NOT EXISTS \"{table}\" ({cols});"
    conn.execute(f"DROP TABLE IF EXISTS \"{table}\";")
    conn.execute(sql)
    conn.commit()


def load_csv(conn: sqlite3.Connection, table: str, csv_path: Path, headers: List[str]) -> None:
    placeholders = ",".join(["?"] * len(headers))
    quoted_columns = ", ".join([f'"{h}"' for h in headers])
    insert_sql = f"INSERT INTO \"{table}\" ({quoted_columns}) VALUES ({placeholders})"
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append([r.get(h, None) if r.get(h, None) != "" else None for h in headers])
        if rows:
            conn.executemany(insert_sql, rows)
            conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Load seed CSVs into a SQLite database")
    parser.add_argument("--db", type=str, required=True, help="SQLite database file path")
    parser.add_argument("--in-dir", type=str, required=True, help="Directory containing *.csv seeds")
    args = parser.parse_args()

    db_path = Path(args.db)
    in_dir = Path(args.in_dir)

    conn = ensure_db(db_path)
    try:
        for csv_path in sorted(in_dir.glob("*.csv")):
            table = csv_path.stem
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    headers = next(reader)
                except StopIteration:
                    continue
            create_table(conn, table, headers)
            load_csv(conn, table, csv_path, headers)
            print(f"Loaded {csv_path.name} -> table {table}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


