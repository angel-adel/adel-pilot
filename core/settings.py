"""Сохранение настроек пользователя (тема и др.)"""
import json
import os
import config


SETTINGS_FILE = os.path.join(config.APP_DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "theme": "dark",  # "dark" или "light"
}


def load_settings() -> dict:
    """Загружает настройки из файла"""
    if not os.path.isfile(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Мержим с дефолтными (на случай добавления новых настроек в будущем)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Сохраняет настройки в файл"""
    os.makedirs(config.APP_DATA_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Settings] Ошибка сохранения: {e}", flush=True)


def get_theme_name() -> str:
    """Возвращает имя текущей темы"""
    return load_settings().get("theme", "dark")


def toggle_theme() -> str:
    """Переключает тему и возвращает новое имя"""
    settings = load_settings()
    current = settings.get("theme", "dark")
    new_theme = "light" if current == "dark" else "dark"
    settings["theme"] = new_theme
    save_settings(settings)
    return new_theme