import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
import config
from ui.main_window import MainWindow, FloatingActionButton
from ui.tray import TrayController
from db.database import init_db

def main():
    # Создаем папку для БД
    os.makedirs(config.APP_DATA_DIR, exist_ok=True)
    
    # Инициализируем БД (убедись, что в новом config.py есть DB_PATH)
    if hasattr(config, 'DB_PATH'):
        init_db(config.DB_PATH)
    
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setQuitOnLastWindowClosed(False) # Чтобы программа не закрывалась при скрытии окна
    
    # 1. Создаем главное окно
    window = MainWindow()
    
    # 2. Создаем плавающую кнопку
    fab = FloatingActionButton(window)
    fab.show()
    
    # 3. ЗАПУСКАЕМ ТРЕЙ
    tray = TrayController()
    tray.request_search.connect(window.show_and_focus)
    tray.request_quit.connect(app.quit)
    
    # Скрываем главное окно при старте
    window.hide()
    
    # Проверка доступности трея
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("Трей недоступен — показываю окно", flush=True)
        window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()