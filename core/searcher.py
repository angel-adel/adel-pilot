import sqlite3

class Searcher:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def search(self, query: str, only_saves: bool = False, limit: int = 200) -> list[dict]:
        # МАГИЯ: убираем дефисы, пробелы и подчеркивания перед поиском
        q = query.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
        
        if len(q) < 2:
            return []
            
        save_filter = "AND is_save = 1" if only_saves else ""
        
        rows = self.conn.execute(f"""
            SELECT path, name, ext, size, mtime, drive,
                   is_save, launch_count, is_dir
            FROM files
            WHERE name_lower LIKE ?
              {save_filter}
            ORDER BY
                CASE
                    WHEN name_lower = ?      THEN 0
                    WHEN name_lower LIKE ?   THEN 1
                    WHEN name_lower LIKE ?   THEN 2
                    ELSE 3
                END,
                launch_count DESC,
                mtime DESC
            LIMIT ?
        """, (f"%{q}%", q, f"{q}%", f"%{q}%", limit)).fetchall()
        
        return [dict(r) for r in rows]

    def stats(self) -> dict:
        total = self.conn.execute(
            "SELECT COUNT(*) AS c FROM files WHERE is_dir = 0"
        ).fetchone()["c"]
        saves = self.conn.execute(
            "SELECT COUNT(*) AS c FROM files WHERE is_dir = 0 AND is_save = 1"
        ).fetchone()["c"]
        return {"total": total, "saves": saves}