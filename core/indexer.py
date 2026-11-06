import os
import sqlite3
from PySide6.QtCore import QObject, Signal
from config import (
    C_ROOT, D_ROOT, APP_DATA_LOCAL,
    ALLOWED_EXTS, EXCLUDE_EXTS, EXCLUDE_DIRS,
    SAVE_FOLDER_NAMES, MAX_DEPTH_IN_APPDATA,
    EXCLUDE_IN_APPDATA, EXCLUDE_IN_SAVES,
    find_custom_roots,
)
from core.scanner import scan_games, scan_projects


class IndexWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(int)
    error = Signal(str)

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self._stop = False

    def stop(self):
        self._stop = True

    def _skip_dir(self, name: str) -> bool:
        if name in EXCLUDE_DIRS:
            return True
        if name.startswith(".") and name not in (".", ".."):
            return True
        return False

    def _file_allowed(self, name: str, is_save_ctx: bool) -> bool:
        ext = os.path.splitext(name)[1].lower()
        if is_save_ctx:
            return ext not in EXCLUDE_IN_SAVES
        if ext in EXCLUDE_EXTS:
            return False
        return ext in ALLOWED_EXTS

    def _walk_root(self, root: str, is_save_ctx: bool):
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            if self._stop:
                return
            dirnames[:] = [d for d in dirnames if not self._skip_dir(d)]
            yield dirpath, filenames, is_save_ctx

    def _find_save_dirs(self, base: str) -> list[str]:
        found = []
        base_depth = base.rstrip("\\").count("\\")
        for dirpath, dirnames, _ in os.walk(base, topdown=True):
            if self._stop:
                return found
            depth = dirpath.count("\\") - base_depth
            if depth >= MAX_DEPTH_IN_APPDATA:
                dirnames[:] = []
                continue
            lower_dirs = {d.lower(): d for d in dirnames}
            hits = [orig for low, orig in lower_dirs.items()
                    if low in SAVE_FOLDER_NAMES]
            for h in hits:
                full = os.path.join(dirpath, h)
                found.append(full)
                dirnames.remove(h)
            dirnames[:] = [
                d for d in dirnames
                if d.lower() not in EXCLUDE_IN_APPDATA
                and not self._skip_dir(d)
            ]
        return found

    def _collect_targets(self):
        targets = []
        if os.path.isdir(D_ROOT):
            targets.append((D_ROOT, False))
        if os.path.isdir(C_ROOT):
            for username in os.listdir(C_ROOT):
                user_path = os.path.join(C_ROOT, username)
                if not os.path.isdir(user_path):
                    continue
                if username in ("Public", "Default", "Default User", "All Users"):
                    continue
                targets.append((user_path, False))
        if os.path.isdir(C_ROOT):
            for username in os.listdir(C_ROOT):
                local = os.path.join(C_ROOT, username, APP_DATA_LOCAL)
                if not os.path.isdir(local):
                    continue
                for save_dir in self._find_save_dirs(local):
                    targets.append((save_dir, True))
        return targets

    def _index_games_and_projects(self, cur):
        """Сканирует папки игр и проектов и добавляет их в БД"""
        # Автоматически находим все папки с играми и проектами на всех дисках
        roots = find_custom_roots()
        
        print(f"[Indexer] Найдено папок с проектами: {len(roots['projects'])}", flush=True)
        print(f"[Indexer] Найдено папок с играми: {len(roots['games'])}", flush=True)
        for p_root in roots['projects']:
            print(f"  📁 {p_root}", flush=True)
        for g_root in roots['games']:
            print(f"  🎮 {g_root}", flush=True)

        # 1. Проекты (сохраняем как папки, is_dir=1)
        projects = scan_projects(roots["projects"])
        print(f"[Indexer] Обнаружено проектов: {len(projects)}", flush=True)
        for p in projects:
            try:
                st = os.stat(p["folder"])
                drive = os.path.splitdrive(p["folder"])[0] or "?"
                cur.execute("""
                    INSERT INTO files (path, name, name_lower, ext, size, mtime, is_dir, drive, is_save, launch_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET name=excluded.name, mtime=excluded.mtime
                """, (p["folder"], p["name"], p["name"].lower(), "", st.st_size, int(st.st_mtime), 1, drive, 0, 0))
            except Exception:
                pass

        # 2. Игры (сохраняем как .exe файлы, is_dir=0)
        games = scan_games(roots["games"])
        print(f"[Indexer] Обнаружено игр: {len(games)}", flush=True)
        for g in games:
            try:
                st = os.stat(g["exe"])
                drive = os.path.splitdrive(g["exe"])[0] or "?"
                cur.execute("""
                    INSERT INTO files (path, name, name_lower, ext, size, mtime, is_dir, drive, is_save, launch_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET name=excluded.name, mtime=excluded.mtime
                """, (g["exe"], g["name"], g["name"].lower(), ".exe", st.st_size, int(st.st_mtime), 0, drive, 0, 0))
            except Exception:
                pass

    def run(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            self.progress.emit(0, 0, "Поиск целей индексации...")
            targets = self._collect_targets()
            
            self.progress.emit(0, 0, "Подсчёт файлов...")
            total = 0
            for root, is_save in targets:
                for _, filenames, _ in self._walk_root(root, is_save):
                    total += 1
                    
            processed = 0
            batch = []
            BATCH_SIZE = 1000
            
            for root, is_save in targets:
                if self._stop:
                    break
                for dirpath, filenames, save_ctx in self._walk_root(root, is_save):
                    if self._stop:
                        break
                    if not save_ctx and "AppData" in dirpath.split(os.sep):
                        continue
                    drive = os.path.splitdrive(dirpath)[0] or "?"
                    for fname in filenames:
                        if not self._file_allowed(fname, save_ctx):
                            continue
                        full = os.path.join(dirpath, fname)
                        try:
                            st = os.stat(full)
                        except OSError:
                            continue
                        ext = os.path.splitext(fname)[1].lower()
                        batch.append((
                            full, fname, fname.lower(), ext,
                            st.st_size, int(st.st_mtime), 0,
                            drive, 1 if save_ctx else 0,
                        ))
                        if len(batch) >= BATCH_SIZE:
                            self._flush(cur, batch)
                            batch.clear()
                            conn.commit()
                    processed += 1
                    self.progress.emit(processed, total, dirpath)
                    
            if batch:
                self._flush(cur, batch)
                
            # Индексация игр и проектов
            self.progress.emit(0, 0, "Индексация игр и проектов...")
            self._index_games_and_projects(cur)
            
            self._cleanup_deleted(cur, targets)
            conn.commit()
            conn.close()
            self.finished.emit(processed)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))

    def _flush(self, cur, batch):
        cur.executemany("""
            INSERT INTO files
                (path, name, name_lower, ext, size, mtime, is_dir, drive, is_save)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                size      = excluded.size,
                mtime     = excluded.mtime,
                is_save   = excluded.is_save
        """, batch)

    def _cleanup_deleted(self, cur, targets):
        cur.execute("SELECT id, path FROM files WHERE is_dir = 0")
        to_delete = []
        for row in cur.fetchall():
            if not os.path.exists(row["path"]):
                to_delete.append((row["id"],))
        if to_delete:
            cur.executemany("DELETE FROM files WHERE id = ?", to_delete)