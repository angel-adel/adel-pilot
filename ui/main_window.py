import os
from urllib.parse import quote, unquote
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLineEdit, QListWidget, QListWidgetItem, QLabel, QTextBrowser,
    QPushButton, QMenu
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QIcon, QPainter, QFont, QColor, QLinearGradient, QAction, QPixmap
from PySide6.QtWidgets import QApplication
import config
from core.ai_agent import AIAgent
from core.searcher import Searcher
from core.project_open import open_in_explorer, open_in_vscode, open_in_android_studio
from core.launcher import launch
from core.themes import DARK_THEME, LIGHT_THEME, get_stylesheet
from core.settings import get_theme_name, toggle_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.resize(1200, 700)
        self.theme = DARK_THEME  # по умолчанию

        if os.path.isfile(config.MAIN_ICON):
            self.setWindowIcon(QIcon(config.MAIN_ICON))

        self.ai_agent = AIAgent(config.DB_PATH)
        self.searcher = Searcher(config.DB_PATH)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- ЛЕВАЯ ПАНЕЛЬ: ЧАТ ---
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        self.chat_history = QTextBrowser()
        self.chat_history.setOpenExternalLinks(False)
        self.chat_history.anchorClicked.connect(self._on_button_clicked)
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Введи искомое слово в чате")
        self.chat_input.returnPressed.connect(self._handle_chat_input)
        chat_layout.addWidget(self.chat_input)

        # Кнопки в ряд (тема + о программе)
        btn_row = QWidget()
        btn_row_layout = QHBoxLayout(btn_row)
        btn_row_layout.setContentsMargins(0, 0, 0, 0)
        btn_row_layout.setSpacing(5)
        btn_row_layout.addStretch()

        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setToolTip("Переключить тему")
        self.btn_theme.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 18px; padding: 5px; }
            QPushButton:hover { background-color: rgba(128,128,128,0.2); border-radius: 4px; }
        """)
        self.btn_theme.clicked.connect(self._toggle_theme)
        btn_row_layout.addWidget(self.btn_theme)

        btn_about = QPushButton("ℹ️")
        btn_about.setToolTip("О программе")
        btn_about.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-size: 18px; padding: 5px; }
            QPushButton:hover { background-color: rgba(128,128,128,0.2); border-radius: 4px; }
        """)
        from ui.about_dialog import AboutDialog
        btn_about.clicked.connect(lambda: AboutDialog(self).exec_())
        btn_row_layout.addWidget(btn_about)

        chat_layout.addWidget(btn_row)
        splitter.addWidget(chat_widget)

        # --- ПРАВАЯ ПАНЕЛЬ: ПОИСК И ПРЕВЬЮ ---
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Быстрый поиск файлов и игр...")
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._handle_search)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(300))
        search_layout.addWidget(self.search_input)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._show_preview)
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self._show_context_menu)
        search_layout.addWidget(self.results_list)

        self.preview_label = QLabel("Предварительный просмотр")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextFormat(Qt.RichText)
        search_layout.addWidget(self.preview_label)

        splitter.addWidget(search_widget)
        splitter.setSizes([600, 600])

        # Применяем сохранённую тему
        self._apply_theme(get_theme_name())
        
        self.ai_thread = QThread()
        self.ai_worker = None

        self._add_chat_message("system", f"Добро пожаловать в {config.APP_NAME} v{config.APP_VERSION}. Я готов к работе.")

    # ==========================================
    # ТЕМЫ
    # ==========================================
    def _apply_theme(self, theme_name: str):
        self.current_theme_name = theme_name
        self.theme = LIGHT_THEME if theme_name == "light" else DARK_THEME
        self.setStyleSheet(get_stylesheet(self.theme))

        if hasattr(self, 'btn_theme'):
            self.btn_theme.setText("☀️" if theme_name == "dark" else "🌙")

        # Обновляем превью
        t = self.theme
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: {t['preview_bg']};
                color: {t['preview_text']};
                border: 1px dashed {t['border_color']};
                border-radius: 8px;
                min-height: 150px;
                font-size: 14px;
            }}
        """)

        # Перерисовываем превью если есть выбор
        current_item = self.results_list.currentItem()
        if current_item:
            self._show_preview(current_item)

    def _toggle_theme(self):
        new_theme = toggle_theme()
        self._apply_theme(new_theme)

    # ==========================================
    # ЧАТ
    # ==========================================
    def _add_chat_message(self, role: str, text: str, options: list = None):
        t = self.theme
        color = t["user_msg"] if role == "user" else t["bot_msg"]
        name = "Ты" if role == "user" else "Ádel"
        html = f'<p style="color: {color}; margin: 10px 0 5px 0;"><b>{name}:</b> {text}</p>'

        if options:
            html += '<div style="margin: 5px 0 15px 0;">'
            for opt in options:
                action = opt['action']
                path = quote(opt['path'], safe='')
                url = f"adel://{action}/{path}"
                html += (f'<a href="{url}" style="background-color: {t["button_bg"]}; '
                         f'color: {t["button_text"]}; padding: 8px 15px; border-radius: 6px; '
                         f'text-decoration: none; margin-right: 8px; display: inline-block; '
                         f'border: 1px solid {t["border_color"]}; cursor: pointer;">'
                         f'{opt["label"]}</a>')
            html += '</div>'

        self.chat_history.append(html)

    def _handle_chat_input(self):
        text = self.chat_input.text().strip()
        if not text:
            return

        self._add_chat_message("user", text)
        self.chat_input.clear()
        self.chat_input.setEnabled(False)

        if not config.is_path_safe(text): 
            self._add_chat_message("system", config.SECURITY_BLOCK_MESSAGE)
            self.chat_input.setEnabled(True)
            return

        self._add_chat_message("system", "Думаю...")

        # Создаем рабочего и отправляем в фоновый поток
        self.ai_worker = AIWorker(self.ai_agent, text)
        self.ai_worker.moveToThread(self.ai_thread)
        
        # Связываем сигналы
        self.ai_thread.started.connect(self.ai_worker.run)
        self.ai_worker.finished.connect(self._on_ai_finished)
        self.ai_worker.finished.connect(self.ai_thread.quit)
        
        # Запускаем поток
        self.ai_thread.start()

    def _on_ai_finished(self, result: dict):
        """Этот метод вызовется, когда ИИ закончит думать"""
        # Очищаем "Думаю..." и показываем результат
        self.chat_history.clear()
        self._add_chat_message("system", result["message"], result.get("options", []))
        
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus()

    def _on_button_clicked(self, url: QUrl):
        url_str = url.toString()
        if url_str.startswith("adel://"):
            rest = url_str[7:]
            if "/" in rest:
                action, path_encoded = rest.split("/", 1)
                path = unquote(path_encoded)
                self._add_chat_message("user", f"Выбрано: {path}")
                try:
                    self._execute_action(action, path)
                    self._add_chat_message("system", f"✅ Действие выполнено: {action}")
                except Exception as e:
                    self._add_chat_message("system", f"❌ Ошибка выполнения: {e}")

    def _execute_action(self, action: str, path: str):
        if not config.is_path_safe(path):
            raise PermissionError(config.SECURITY_BLOCK_MESSAGE)
        if action == "open_in_explorer":
            open_in_explorer(path)
        elif action == "open_in_vscode":
            open_in_vscode(path)
        elif action == "open_in_android_studio":
            open_in_android_studio(path)
        elif action == "launch_file":
            launch(path, config.DB_PATH)
        else:
            raise ValueError(f"Неизвестное действие: {action}")

    def show_and_focus(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        self.chat_input.setFocus()
        self.chat_input.selectAll()

    # ==========================================
    # ПРАВАЯ ПАНЕЛЬ
    # ==========================================
    def _handle_search(self):
        query = self.search_input.text().strip()
        self.results_list.clear()

        if len(query) < 2:
            self.preview_label.setText("Введите минимум 2 символа для поиска")
            return

        normalized = query.lower().replace("-", "").replace("_", "").replace(" ", "")
        results = self.searcher.search(normalized, only_saves=False, limit=20)

        if not results:
            self.preview_label.setText("Ничего не найдено")
            return

        for row in results:
            item = QListWidgetItem()
            icon = "📁" if row.get("is_dir", 0) else "📄"
            item.setText(f"{icon} {row['name']}")
            item.setData(Qt.UserRole, row)
            self.results_list.addItem(item)

    def _show_preview(self, item: QListWidgetItem):
        row = item.data(Qt.UserRole)
        if not row:
            return

        path = row["path"]
        name = row["name"]
        is_dir = row.get("is_dir", 0)
        ext = row.get("ext", "").lower()
        size = row.get("size", 0)
        mtime = row.get("mtime", 0)

        from datetime import datetime
        date_str = datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M") if mtime else "Неизвестно"
        size_str = self._format_size(size)

        t = self.theme
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"}
        text_exts = {".txt", ".py", ".js", ".json", ".xml", ".yaml", ".yml", ".md", ".html",
                     ".css", ".java", ".kt", ".cpp", ".c", ".h", ".cs", ".ini", ".cfg", ".log"}

        if is_dir:
            try:
                file_count = len(os.listdir(path))
            except Exception:
                file_count = "Ошибка"
            html = (f'<div style="padding: 20px; text-align: center;">'
                    f'<div style="font-size: 48px; margin-bottom: 10px;">📁</div>'
                    f'<div style="font-size: 18px; font-weight: bold; color: {t["text_color"]}; margin-bottom: 10px;">{name}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Путь: {path}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Файлов внутри: {file_count}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Изменено: {date_str}</div>'
                    f'</div>')
            self.preview_label.setText(html)

        elif ext in image_exts and os.path.isfile(path):
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    target_width = max(100, self.preview_label.width() - 40)
                    target_height = max(100, self.preview_label.height() - 40)
                    scaled = pixmap.scaled(target_width, target_height,
                                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)
                    self.preview_label.setText("")
                    self.preview_label.setAlignment(Qt.AlignCenter)
                else:
                    self.preview_label.setText("Не удалось загрузить изображение")
            except Exception as e:
                self.preview_label.setText(f"Ошибка загрузки: {e}")

        elif ext in text_exts and os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html = (f'<div style="padding: 15px;">'
                        f'<div style="font-size: 16px; font-weight: bold; color: {t["text_color"]}; margin-bottom: 10px;">📄 {name}</div>'
                        f'<div style="color: {t["secondary_text"]}; font-size: 12px; margin-bottom: 10px;">{path} ({size_str})</div>'
                        f'<pre style="background-color: {t["code_bg"]}; color: {t["code_text"]}; padding: 10px; '
                        f'border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; '
                        f'overflow-x: auto; max-height: 300px; overflow-y: auto;">{content}</pre>'
                        f'</div>')
                self.preview_label.setText(html)
            except Exception as e:
                self.preview_label.setText(f"Ошибка чтения файла: {e}")

        else:
            icon = self._get_file_icon(ext)
            html = (f'<div style="padding: 20px; text-align: center;">'
                    f'<div style="font-size: 48px; margin-bottom: 10px;">{icon}</div>'
                    f'<div style="font-size: 18px; font-weight: bold; color: {t["text_color"]}; margin-bottom: 10px;">{name}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Путь: {path}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Размер: {size_str}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Тип: {ext if ext else "Неизвестно"}</div>'
                    f'<div style="color: {t["secondary_text"]}; font-size: 13px;">Изменено: {date_str}</div>'
                    f'</div>')
            self.preview_label.setText(html)

    def _show_context_menu(self, position):
        item = self.results_list.itemAt(position)
        if not item:
            return
        row = item.data(Qt.UserRole)
        if not row:
            return

        path = row["path"]
        is_dir = row.get("is_dir", 0)

        menu = QMenu(self)
        if is_dir:
            menu.addAction("📂 Открыть папку", lambda: open_in_explorer(path))
            menu.addAction("💻 Открыть в VS Code", lambda: open_in_vscode(path))
            menu.addAction("🤖 Открыть в Android Studio", lambda: open_in_android_studio(path))
        else:
            menu.addAction("🚀 Запустить/Открыть", lambda: launch(path, config.DB_PATH))
            menu.addAction("📂 Показать в папке", lambda: open_in_explorer(os.path.dirname(path)))
        menu.addSeparator()
        menu.addAction("📋 Копировать путь", lambda: QApplication.clipboard().setText(path))
        menu.exec_(self.results_list.viewport().mapToGlobal(position))

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} Б"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} КБ"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} МБ"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} ГБ"

    def _get_file_icon(self, ext: str) -> str:
        icons = {
            ".exe": "🚀", ".bat": "⚙️", ".cmd": "⚙️",
            ".pdf": "📕", ".doc": "📘", ".docx": "📘",
            ".zip": "📦", ".rar": "📦", ".7z": "📦",
            ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵",
            ".mp4": "🎬", ".mkv": "🎬", ".avi": "🎬",
            ".py": "🐍", ".js": "🟨", ".java": "☕", ".kt": "🟣",
        }
        return icons.get(ext, "📄")


class FloatingActionButton(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(64, 64)

        screen = self.main_window.screen().geometry()
        self.move(screen.width() - 100, screen.height() - 100)

        self._drag_start_pos = None
        self._was_dragged = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#6a11cb"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 64, 64)
        font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(self.rect(), Qt.AlignCenter, "A")
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.globalPos()
            self._was_dragged = False

    def mouseMoveEvent(self, event):
        if self._drag_start_pos and (event.buttons() & Qt.LeftButton):
            distance = (event.globalPos() - self._drag_start_pos).manhattanLength()
            if distance > QApplication.startDragDistance():
                self._was_dragged = True
                self.move(self.pos() + event.globalPos() - self._drag_start_pos)
                self._drag_start_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self._was_dragged:
                self.main_window.show_and_focus()
            self._drag_start_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            QApplication.quit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(f"Открыть {config.APP_NAME}", self.main_window.show_and_focus)
        menu.addSeparator()
        menu.addAction("Завершить работу", QApplication.quit)
        menu.exec_(event.globalPos())