import sqlite3
import config

conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = sqlite3.Row

print("📂 ВСЕ ПРОЕКТЫ (ПАПКИ) В БАЗЕ:")
rows = conn.execute("SELECT name, path FROM files WHERE is_dir = 1").fetchall()
if rows:
    for r in rows:
        print(f"  📁 {r['name']} -> {r['path']}")
else:
    print("  (Папок не найдено. Индексатор не смог их добавить)")

print("\n🔍 ПОИСК СЛОВА 'CONNECT' (ВСЁ, ЧТО ЕСТЬ):")
rows = conn.execute("SELECT name, path, is_dir FROM files WHERE name_lower LIKE '%connect%'").fetchall()
if rows:
    for r in rows:
        icon = "📁" if r['is_dir'] else "📄"
        print(f"  {icon} {r['name']} -> {r['path']}")
else:
    print("  (Слово 'connect' вообще не встречается в базе)")

conn.close()
input("\nНажми Enter, чтобы выйти...")