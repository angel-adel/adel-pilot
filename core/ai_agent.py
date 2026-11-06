import json
import os
import re
from llama_cpp import Llama
from core.searcher import Searcher
from core.project_open import open_in_explorer, open_in_vscode, open_in_android_studio
from core.launcher import launch
import config


class AIAgent:
    def __init__(self, db_path: str):
        model_path = config.resource_path("models/qwen2.5-1.5b-instruct-q4_k_m.gguf")
        print(f"[AI] Загрузка модели...", flush=True)
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
        print(f"[AI] Модель загружена.", flush=True)
        
        self.searcher = Searcher(db_path)
        self.db_path = db_path
        
        # Мусорные расширения, которые не нужно показывать
        self.junk_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ini", ".cfg", 
                         ".zip", ".rar", ".7z", ".tar", ".gz", ".torrent", ".log", ".txt"}

    def extract_keywords(self, query: str) -> str:
        stop_words = {"открой", "запусти", "покажи", "найди", "включи", "открыть", "запустить", 
                      "в", "на", "для", "с", "по", "из", "у", "к", "о", "об", "и", "или", 
                      "а", "но", "мой", "твой", "проект", "игру", "папку", "файл", "программу"}
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return " ".join(keywords) if keywords else query

    def _find_exe_in_folder(self, folder_path: str, max_depth: int = 2) -> str | None:
        """Ищет первый .exe файл внутри папки (неглубоко)"""
        try:
            base_depth = folder_path.rstrip("\\").count("\\")
            for dirpath, _, filenames in os.walk(folder_path):
                depth = dirpath.count("\\") - base_depth
                if depth > max_depth:
                    break
                for fname in filenames:
                    if fname.lower().endswith(".exe"):
                        return os.path.join(dirpath, fname)
        except Exception:
            pass
        return None

    def get_context(self, query: str, limit: int = 10) -> list:
        clean_query = self.extract_keywords(query)
        results = self.searcher.search(clean_query, only_saves=False, limit=limit)
        
        context = []
        for row in results:
            ext = row.get("ext", "").lower()
            # Фильтруем мусор
            if ext in self.junk_exts:
                continue
                
            item = {
                "name": row["name"],
                "path": row["path"],
                "ext": ext,
                "is_dir": row.get("is_dir", 0)
            }
            # Если это папка — ищем внутри .exe файл
            if item["is_dir"]:
                exe_path = self._find_exe_in_folder(item["path"])
                item["has_exe"] = exe_path is not None
                item["exe_path"] = exe_path or ""
            else:
                item["has_exe"] = False
                item["exe_path"] = ""
            context.append(item)
        
        # Сортируем: сначала .exe файлы и папки с .exe, потом остальное
        context.sort(key=lambda x: (
            0 if x["ext"] == ".exe" or x.get("has_exe") else 1,
            x["name"]
        ))
        
        return context[:5]  # Ограничиваем до 5 релевантных результатов

    def _is_path_allowed(self, path: str, context: list) -> bool:
        """Проверяет, разрешён ли путь (с учётом родительских папок)"""
        path_lower = path.lower().replace("\\", "/")
        
        for item in context:
            item_path_lower = item["path"].lower().replace("\\", "/")
            if path_lower == item_path_lower:
                return True
            if item_path_lower.startswith(path_lower + "/"):
                return True
            if path_lower.startswith(item_path_lower + "/"):
                return True
            if item.get("exe_path"):
                exe_lower = item["exe_path"].lower().replace("\\", "/")
                if path_lower == exe_lower:
                    return True
                if exe_lower.startswith(path_lower + "/"):
                    return True
        return False

    def process_request(self, user_input: str) -> dict:
        print(f"\n[AI DEBUG] Запрос пользователя: '{user_input}'", flush=True)
        context = self.get_context(user_input)
        print(f"[AI DEBUG] Найдено в Searcher: {len(context)} элементов (после фильтрации)", flush=True)
        
        if not context:
            return {"message": "К сожалению, я ничего не нашел по твоему запросу в индексе.", "options": []}

        for c in context:
            exe_info = f" [внутри есть .exe: {c['exe_path']}]" if c.get("has_exe") else ""
            print(f"  - {c['name']} ({c['ext']}) : {c['path']}{exe_info}", flush=True)

        # Формируем читаемый контекст для модели
        context_lines = []
        for item in context:
            if item["is_dir"]:
                exe_note = f", ВНУТРИ ЕСТЬ .exe ({item['exe_path']})" if item.get("has_exe") else ""
                context_lines.append(f"- ПАПКА: {item['name']} (путь: {item['path']}{exe_note})")
            elif item["ext"] == ".exe":
                context_lines.append(f"- ИГРА/ПРОГРАММА: {item['name']} (путь: {item['path']})")
            else:
                context_lines.append(f"- ФАЙЛ: {item['name']} (путь: {item['path']}, расширение: {item['ext']})")
        context_str = "\n".join(context_lines)

        system_prompt = f"""Ты — помощник Ádel Pilot. Твоя задача — выбрать действия для найденных элементов.

Найдено в базе:
{context_str}

ПРАВИЛА:
1. Если найдена ПАПКА с пометкой "ВНУТРИ ЕСТЬ .exe" — это игра или программа. Предложи:
   - "📂 Папка" (action: open_in_explorer, path: путь к папке)
   - "🚀 Запустить" (action: launch_file, path: путь к .exe из скобок)
2. Если найдена ПАПКА БЕЗ .exe — это проект. Предложи:
   - "📂 Папка" (action: open_in_explorer, path: путь к папке)
   - "💻 VS Code" (action: open_in_vscode, path: путь к папке)
   - "🤖 Android Studio" (action: open_in_android_studio, path: путь к папке)
3. Если найден .exe ФАЙЛ — это игра или программа. Предложи:
   - "🚀 Запустить" (action: launch_file, path: путь к файлу)
4. Никогда не предлагай запуск для архивов (.zip, .rar), документов или картинок!
5. Никогда не пиши "ничего не найдено", если список не пуст!

ПРИМЕР ДЛЯ ИГРЫ (папка с .exe):
{{"message": "Нашёл игру. Что открыть?", "options": [
  {{"label": "📂 Папка", "action": "open_in_explorer", "path": "D:\\\\Games\\\\MyGame"}},
  {{"label": "🚀 Запустить", "action": "launch_file", "path": "D:\\\\Games\\\\MyGame\\\\game.exe"}}
]}}

Верни СТРОГО JSON в формате:
{{"message": "Твой короткий ответ", "options": [{{"label": "Текст кнопки", "action": "название_действия", "path": "точный_путь"}}]}}"""

        try:
            response = self.llm.create_chat_completion(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                temperature=0.1, max_tokens=500
            )
            content = response["choices"][0]["message"].get("content", "")
            print(f"[AI DEBUG] Сырой ответ модели:\n{content.strip()}", flush=True)
            
            json_match = re.search(r'\{.*"options".*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                safe_options = []
                for opt in data.get("options", []):
                    path = opt.get("path", "")
                    
                    if not config.is_path_safe(path):
                        print(f"[AI DEBUG] Путь заблокирован безопасностью: {path}", flush=True)
                        continue
                    
                    if self._is_path_allowed(path, context):
                        safe_options.append(opt)
                    else:
                        print(f"[AI DEBUG] Путь отклонен (нет в контексте): {path}", flush=True)
                
                # Автодобавление кнопки "Запустить" для папок с .exe
                has_launch_button = any(opt["action"] == "launch_file" for opt in safe_options)
                if not has_launch_button:
                    for item in context:
                        if item.get("has_exe") and item["exe_path"]:
                            safe_options.append({
                                "label": "🚀 Запустить",
                                "action": "launch_file",
                                "path": item["exe_path"]
                            })
                            print(f"[AI DEBUG] Автодобавлена кнопка запуска: {item['exe_path']}", flush=True)
                            break
                
                data["options"] = safe_options
                print(f"[AI DEBUG] Итоговых безопасных опций: {len(safe_options)}", flush=True)
                return data
            else:
                print("[AI DEBUG] JSON не найден в ответе модели", flush=True)
                return {"message": "ИИ запутался и не смог сформировать ответ.", "options": []}
                
        except Exception as e:
            print(f"[AI DEBUG] Ошибка: {e}", flush=True)
            return {"message": f"Ошибка модуля ИИ: {str(e)}", "options": []}

    def execute_action(self, action: str, path: str):
        print(f"[AI] Выполняю: {action} -> {path}", flush=True)
        if action == "open_in_explorer":
            open_in_explorer(path)
        elif action == "open_in_vscode":
            open_in_vscode(path)
        elif action == "open_in_android_studio":
            open_in_android_studio(path)
        elif action == "launch_file":
            launch(path, self.db_path)