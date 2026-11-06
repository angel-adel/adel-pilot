import os
import sys
from PySide6.QtCore import QCoreApplication
import config
from db.database import init_db
from core.indexer import IndexWorker

def main():
    # Инициализируем минимальное Qt-приложение для работы сигналов
    app = QCoreApplication(sys.argv)
    
    # Создаем папку и инициализируем БД
    os.makedirs(config.APP_DATA_DIR, exist_ok=True)
    init_db(config.DB_PATH)
    
    print("🚀 Запуск индексации файлов и проектов...")
    print("Это может занять от нескольких секунд до пары минут. Пожалуйста, подождите.\n")
    
    worker = IndexWorker(config.DB_PATH)
    
    # Выводим прогресс в консоль
    worker.progress.connect(lambda cur, total, path: print(f"⏳ Сканирование: {cur}/{total} | {path[-60:]}", end='\r'))
    
    def on_finished(count):
        print(f"\n✅ Индексация успешно завершена! Обработано элементов: {count}")
        print(f"💾 База данных сохранена в: {config.DB_PATH}")
        app.quit()
        
    def on_error(msg):
        print(f"\n❌ Ошибка при индексации: {msg}")
        app.quit()

    worker.finished.connect(on_finished)
    worker.error.connect(on_error)
    
    # Запускаем процесс (для консольного скрипта синхронный запуск вполне подходит)
    worker.run()

if __name__ == "__main__":
    main()