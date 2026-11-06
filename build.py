import os
import sys
import subprocess

def build():
    print("🚀 Начинаю сборку Ádel Pilot...")
    
    # ИСПРАВЛЕНО: используем sys.executable и -m PyInstaller
    # Это гарантирует, что сборщик запустится через твой текущий Python
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",  # Используем папку (стабильнее для модели 900МБ)
        "--windowed", # Убрать черную консоль при запуске
        "--name", "AdelPilot",
        "--icon", "assets/adel_pilot.png",
        "--collect-all", "llama_cpp", # Тянет все DLL для ИИ
        "--collect-all", "PySide6",   # Тянет все DLL для интерфейса
        "--add-data", "assets;assets",
        "--add-data", "models;models",
        "--hidden-import", "sqlite3",
        "main.py"
    ]
    
    try:
        subprocess.run(command, check=True)
        print("\n✅ Сборка успешна! Папка dist/AdelPilot готова к распространению.")
        print("⚠️  Проверь, что папки models и assets попали внутрь dist/AdelPilot/")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка сборки: {e}")

if __name__ == "__main__":
    build()