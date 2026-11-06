import string
import os
import sys

# ==========================================
# ОСНОВНЫЕ НАСТРОЙКИ ÁDEL PILOT
# ==========================================
APP_VERSION = "0.001"
APP_NAME = "Ádel Pilot"

# ==========================================
# РЕСУРСЫ (работает и в скрипте, и в exe)
# ==========================================
def resource_path(rel: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel)

ASSETS_DIR = resource_path("assets")
MAIN_ICON = os.path.join(ASSETS_DIR, "adel_pilot.ico")
FAB_ICON = os.path.join(ASSETS_DIR, "adel_pilot.png")
TRAY_ICON = os.path.join(ASSETS_DIR, "adel_pilot.png")  # PNG для трея

# ==========================================
# УНИВЕРСАЛЬНЫЕ ПУТИ
# ==========================================
USER_HOME = os.path.expanduser("~")

if sys.platform == "win32":
    SYSTEM_DRIVE = os.environ.get("SystemDrive", "C:")
    LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", os.path.join(USER_HOME, "AppData", "Local"))
    APP_DATA_DIR = os.path.join(LOCAL_APPDATA, "AdelPilot")
else:
    SYSTEM_DRIVE = "/"
    LOCAL_APPDATA = os.path.join(USER_HOME, ".config")
    APP_DATA_DIR = os.path.join(LOCAL_APPDATA, "AdelPilot")

DB_PATH = os.path.join(APP_DATA_DIR, "pilot.db")

# ==========================================
# СТАРЫЕ КОНСТАНТЫ ДЛЯ ИНДЕКСАТОРА (нужны indexer.py)
# ==========================================
C_ROOT = r"C:\Users"
D_ROOT = "D:\\"
APP_DATA_LOCAL = r"AppData\Local"

# Игры и проекты
TARGET_FOLDER_NAMES = {"games", "projects", "игры", "проекты", "game", "project"}

def find_custom_roots() -> dict:
    """Автоматически ищет папки с играми и проектами на всех дисках"""
    games_roots = []
    projects_roots = []
    
    # Получаем все доступные диски (Windows)
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.isdir(f"{d}:\\")]
    
    for drive in drives:
        try:
            for item in os.listdir(drive):
                if item.lower() in TARGET_FOLDER_NAMES:
                    full_path = os.path.join(drive, item)
                    if os.path.isdir(full_path):
                        if "game" in item.lower() or "игр" in item.lower():
                            games_roots.append(full_path)
                        elif "project" in item.lower() or "проект" in item.lower():
                            projects_roots.append(full_path)
        except PermissionError:
            continue
    
    # Фоллбэк: если ничего не нашли, используем старые пути (для твоего ПК)
    if not games_roots and os.path.isdir(r"D:\Games"):
        games_roots.append(r"D:\Games")
    if not projects_roots and os.path.isdir(r"D:\Projects"):
        projects_roots.append(r"D:\Projects")
        
    return {"games": games_roots, "projects": projects_roots}

GAMES_IGNORE = {
    "logs", "_cache", "cache", "temp", "tmp",
    "redist", "redistributables", "_redist", "commonredist",
    "directx", "dotnet", "vcredist",
    "$recycle.bin", "system volume information",
}

PROJECTS_IGNORE = {
    "node_modules", ".git", ".idea", ".vscode",
    "$recycle.bin", "system volume information",
}

EXE_IGNORE_NAMES = {
    "unins000.exe", "uninstall.exe", "setup.exe", "install.exe",
    "vcredist_x64.exe", "vcredist_x86.exe", "dxsetup.exe",
    "directx.exe", "dotnetfx.exe", "crashpad_handler.exe",
    "crashreporter.exe", "notification_helper.exe",
    "unitycrashhandler.exe", "unitycrashhandler64.exe",
    "launcher_installer.exe", "activation.exe", "upc.exe",
    "easyanticheat.exe", "easyanticheat_setup.exe",
    "beservice.exe", "beservice_x64.exe",
}

# Белый / чёрный список расширений
ALLOWED_EXTS = {
    ".exe", ".lnk", ".msi", ".bat", ".cmd",
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".txt", ".rtf", ".odt", ".csv",
    ".sav", ".save", ".savf", ".uesave", ".slot", ".profile", ".es3",
    ".cfg", ".ini", ".json", ".xml", ".yaml", ".yml", ".toml",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff",
    ".svg", ".heic", ".raw",
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
    ".iso", ".torrent", ".url",
}

EXCLUDE_EXTS = {
    ".dll", ".sys", ".drv", ".mui", ".cat", ".inf", ".ocx",
    ".tmp", ".temp", ".log", ".bak", ".old",
    ".pdb", ".obj", ".lib", ".exp", ".ilk",
    ".pyc", ".pyo", ".class",
    ".lock", ".crdownload", ".part",
}

# Исключения при обходе
EXCLUDE_DIRS = {
    "$Recycle.Bin", "System Volume Information", "Recovery",
    "Windows", "ProgramData", "Program Files", "Program Files (x86)",
    "AppData",
    "node_modules", ".git", ".venv", "venv", "__pycache__",
    ".cache", ".gradle", ".m2", ".nuget", ".idea", ".vscode",
    "Temp", "tmp", "Cache", "Logs", "CrashDumps",
}

# AppData\Local — поиск сохранений
SAVE_FOLDER_NAMES = {
    "saved games", "savegames", "saves", "savedata", "save data",
    "savegame", "saved", "save", "profiles",
}

MAX_DEPTH_IN_APPDATA = 4

EXCLUDE_IN_APPDATA = {
    "cache", "temp", "tmp", "logs", "crash", "crashdumps",
    "shadercache", "shaders", "downloads", "updates", "installer",
    "microsoft", "google", "mozilla", "nvidia", "amd", "intel",
    "packages",
}

EXCLUDE_IN_SAVES = {
    ".log", ".tmp", ".temp", ".dmp", ".mdmp", ".crash",
}

# ==========================================
# IDE
# ==========================================
VSCODE_EXE = "code.cmd"
ANDROID_STUDIO_EXE = r"C:\Program Files\Android\Android Studio\bin\studio64.exe"

# ==========================================
# ПОЛИТИКА БЕЗОПАСНОСТИ (Чёрный список)
# ==========================================
FORBIDDEN_PATHS = [
    r"\windows", r"\system32", r"\syswow64", r"\programdata",
    r"\program files", r"\program files (x86)", r"\$recycle.bin",
    r"\system volume information", r"\recovery", r"\boot",
    "pagefile.sys", "hiberfil.sys", "bootmgr", "ntldr", "boot.ini",
    "sam", "system", "security", "software", "components",
    "hkey_local_machine", "hkey_classes_root", "hkey_current_user",
    "hkey_users", "hkey_current_config",
    "/etc", "/bin", "/sbin", "/usr", "/var", "/proc", "/sys", "/dev",
    "/system", "/library", "/private"
]

SECURITY_BLOCK_MESSAGE = "Простите, доступ запрещен политикой безопасности и разработчиком ПО."

def is_path_safe(path: str) -> bool:
    """Умная проверка пути на наличие в чёрном списке"""
    if not path:
        return False
        
    path_lower = path.lower().replace("\\", "/")
    
    # 1. Блокировка веток реестра
    if path_lower.startswith("hkey_"):
        return False
        
    # Разбиваем путь на сегменты для точной проверки
    path_segments = path_lower.split("/")
    
    for forbidden in FORBIDDEN_PATHS:
        forbidden_norm = forbidden.lower().replace("\\", "/")
        
        # 2. Linux системные папки (/bin, /sys, /etc) — проверяем ТОЧНОЕ совпадение сегмента
        # (чтобы /bin не блокировал /binaries)
        if forbidden_norm.startswith("/"):
            folder_name = forbidden_norm.lstrip("/")
            if folder_name in path_segments:
                return False
                
        # 3. Файлы реестра и системные файлы (SAM, SYSTEM, SOFTWARE) — проверяем имя файла в конце
        elif forbidden_norm in ("sam", "system", "security", "software", "components"):
            file_name = path_segments[-1]
            if file_name == forbidden_norm or file_name.startswith(f"{forbidden_norm}."):
                return False
                
        # 4. Остальные системные папки и файлы Windows (\windows, \system32, pagefile.sys)
        else:
            if forbidden_norm in path_lower:
                # Если это файл (с точкой) или начинается с обратного слеша — блокируем
                if "." in forbidden_norm or forbidden_norm.startswith("\\"):
                    return False
                # Для папок (program files) проверяем границы, чтобы не блокировать "my program files backup"
                if f"/{forbidden_norm}/" in path_lower or path_lower.startswith(f"{forbidden_norm}/") or path_lower.endswith(f"/{forbidden_norm}"):
                    return False
                    
    return True