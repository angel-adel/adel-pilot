import os
from config import GAMES_IGNORE, PROJECTS_IGNORE, EXE_IGNORE_NAMES

def _find_main_exe(folder: str, max_depth: int = 3) -> str | None:
    candidates = []
    base_depth = folder.rstrip("\\").count("\\")
    for dirpath, dirnames, filenames in os.walk(folder, topdown=True):
        depth = dirpath.count("\\") - base_depth
        if depth > max_depth:
            dirnames[:] = []
            continue
        for fname in filenames:
            if not fname.lower().endswith(".exe"):
                continue
            if fname.lower() in EXE_IGNORE_NAMES:
                continue
            full = os.path.join(dirpath, fname)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            candidates.append((size, full))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]

def scan_games(games_roots: list[str]) -> list[dict]:
    games = []
    for games_root in games_roots:
        if not os.path.isdir(games_root):
            continue
        for name in sorted(os.listdir(games_root)):
            folder = os.path.join(games_root, name)
            if not os.path.isdir(folder):
                continue
            if name.lower() in GAMES_IGNORE:
                continue
            exe = _find_main_exe(folder)
            if not exe:
                continue
            games.append({"name": name, "folder": folder, "exe": exe})
    return games

def scan_projects(projects_roots: list[str]) -> list[dict]:
    projects = []
    for projects_root in projects_roots:
        if not os.path.isdir(projects_root):
            continue
        for name in sorted(os.listdir(projects_root)):
            folder = os.path.join(projects_root, name)
            if not os.path.isdir(folder):
                continue
            if name.lower() in PROJECTS_IGNORE:
                continue
            projects.append({"name": name, "folder": folder})
    return projects