# db/database.py
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id           INTEGER PRIMARY KEY,
    path         TEXT UNIQUE NOT NULL,
    name         TEXT NOT NULL,
    name_lower   TEXT NOT NULL,
    ext          TEXT,
    size         INTEGER,
    mtime        INTEGER,
    is_dir       INTEGER DEFAULT 0,
    drive        TEXT,
    is_save      INTEGER DEFAULT 0,
    launch_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_name_lower ON files(name_lower);
CREATE INDEX IF NOT EXISTS idx_ext        ON files(ext);
CREATE INDEX IF NOT EXISTS idx_is_save    ON files(is_save);
CREATE INDEX IF NOT EXISTS idx_launch     ON files(launch_count);
"""


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()