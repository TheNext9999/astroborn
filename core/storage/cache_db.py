"""
core/storage/cache_db.py
Lớp lưu trữ nhẹ bằng SQLite cho AstroBorn, gồm 2 việc:

1. Cache kết quả NASA APOD theo ngày -> giảm số lần gọi API thật,
   tăng tốc độ tải lại cho các ngày sinh đã được tra cứu trước đó.
2. Lưu trữ "Wall of Stars" - những Bức thư từ Vũ trụ mà người dùng
   đồng ý chia sẻ công khai (ẩn danh) để lan tỏa trên trang.

Không cần cài thêm gì - sqlite3 có sẵn trong Python.
"""

import datetime
import os
import sqlite3
from contextlib import contextmanager

# data/ nằm ở gốc dự án (2 cấp trên module này: core/storage/ -> core/ -> gốc)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "astroborn.db")


def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def _connect():
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_cache (
                date TEXT PRIMARY KEY,
                title TEXT,
                explanation TEXT,
                url TEXT,
                media_type TEXT,
                copyright TEXT,
                source TEXT,
                fetched_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wall_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                display_name TEXT,
                letter TEXT,
                snapshot_title TEXT,
                snapshot_url TEXT
            )
            """
        )


def get_cached_snapshot(date_str: str):
    """Trả về snapshot đã cache cho một ngày cụ thể (YYYY-MM-DD), hoặc None."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM snapshot_cache WHERE date = ?", (date_str,)
        ).fetchone()
        if row:
            return {
                "title": row["title"],
                "explanation": row["explanation"],
                "url": row["url"],
                "media_type": row["media_type"],
                "date": row["date"],
                "copyright": row["copyright"],
                "source": "cache",
            }
    return None


def save_snapshot(date_str: str, snapshot: dict):
    """Lưu snapshot vào cache (ghi đè nếu ngày đó đã tồn tại)."""
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO snapshot_cache
                (date, title, explanation, url, media_type, copyright, source, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date_str,
                snapshot.get("title", ""),
                snapshot.get("explanation", ""),
                snapshot.get("url", ""),
                snapshot.get("media_type", "image"),
                snapshot.get("copyright", "NASA / APOD"),
                snapshot.get("source", "live"),
                datetime.datetime.now().isoformat(timespec="seconds"),
            ),
        )


def add_wall_entry(display_name: str, letter: str, snapshot_title: str, snapshot_url: str):
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO wall_entries (created_at, display_name, letter, snapshot_title, snapshot_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.datetime.now().isoformat(timespec="seconds"),
                display_name or "Một lữ khách ẩn danh",
                letter,
                snapshot_title,
                snapshot_url,
            ),
        )


def get_wall_entries(limit: int = 30):
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM wall_entries ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def cache_stats() -> dict:
    """Thống kê nhỏ để hiển thị (số ngày đã cache, số thư trên Wall)."""
    init_db()
    with _connect() as conn:
        snap_count = conn.execute("SELECT COUNT(*) c FROM snapshot_cache").fetchone()["c"]
        wall_count = conn.execute("SELECT COUNT(*) c FROM wall_entries").fetchone()["c"]
        return {"cached_snapshots": snap_count, "wall_entries": wall_count}
