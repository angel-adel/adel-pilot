import sqlite3
import config

conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = sqlite3.Row

print("🔍 Ищем что-нибудь похожее на 'connect', 'smart', 'social' или 'project':")
rows = conn.execute("""
    SELECT name, path, is_dir 
    FROM files 
    WHERE name_lower LIKE '%connect%' 
       OR name_lower LIKE '%smart%' 
       OR name_lower LIKE '%social%'
       OR name_lower LIKE '%project%'
    LIMIT 10
""").fetchall()

if rows:
    for r in rows:
        print(f"  [{'📁 Папка' if r['is_dir'] else '📄 Файл'}] {r['name']} -> {r['path']}")
else:
    print("  Ничего не найдено. Проекты точно лежат в другой папке.")

print("\n📂 Последние 5 добавленных элементов в базу (чтобы понять, куда он смотрел):")
last = conn.execute("SELECT name, path, is_dir FROM files ORDER BY mtime DESC LIMIT 5").fetchall()
for r in last:
    print(f"  [{'📁 Папка' if r['is_dir'] else '📄 Файл'}] {r['name']} -> {r['path']}")

conn.close()