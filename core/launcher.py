# core/launcher.py
import os
import subprocess
import sqlite3
from pathlib import Path


def launch(path: str, db_path: str | None = None):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Не найдено: {path}")

    ext = p.suffix.lower()

    if ext in (".exe", ".bat", ".cmd"):
        subprocess.Popen([str(p)], cwd=str(p.parent))
    else:
        os.startfile(str(p))

    if db_path:
        try:
            conn = sqlite3.connect(db_path)
            conn.execute(
                "UPDATE files SET launch_count = launch_count + 1 "
                "WHERE path = ?", (str(p),)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass