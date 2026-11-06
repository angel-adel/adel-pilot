import config
from core.searcher import Searcher

db = config.DB_PATH
s = Searcher(db)

print(f"🔍 Тестируем поиск в базе: {db}\n")

q1 = "S-Connect"
res1 = s.search(q1)
print(f"1. Поиск '{q1}': найдено {len(res1)}")
for r in res1: 
    print(f"   -> {r['name']} ({r['path']})")

q2 = "SConnect"
res2 = s.search(q2)
print(f"\n2. Поиск '{q2}': найдено {len(res2)}")
for r in res2: 
    print(f"   -> {r['name']} ({r['path']})")