import os
from PySide6.QtCore import QThread
from core.ai_worker import AIWorker
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
import config
from core.themes import DARK_THEME, LIGHT_THEME
from core.settings import get_theme_name


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"О программе {config.APP_NAME}")
        self.setFixedSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        if os.path.isfile(config.MAIN_ICON):
            self.setWindowIcon(QIcon(config.MAIN_ICON))

        theme_name = get_theme_name()
        theme = LIGHT_THEME if theme_name == "light" else DARK_THEME

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Логотип
        logo_label = QLabel()
        if os.path.isfile(config.FAB_ICON):
            pixmap = QPixmap(config.FAB_ICON).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Название и версия
        title_label = QLabel(f"<h2 style='color: {theme['text_color']}; margin: 0;'>{config.APP_NAME}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel(f"<p style='color: {theme['secondary_text']}; font-size: 14px; margin: 0;'>Версия {config.APP_VERSION}</p>")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {theme['border_color']};")
        layout.addWidget(line)

        # Описание
        desc_label = QLabel(
            f"<p style='color: {theme['text_color']}; font-size: 13px; text-align: center;'>"
            "Умный ассистент для управления проектами, играми и файлами.<br>"
            "Использует локальный ИИ для интеллектуального поиска и запуска приложений."
            "</p>"
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        # Ссылки
        links_layout = QHBoxLayout()
        links_layout.setSpacing(15)

        btn_portfolio = QPushButton("🌐 Портфолио")
        btn_portfolio.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border: 1px solid {theme['border_color']};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {theme['hover_bg']}; }}
        """)
        btn_portfolio.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://angel-adel.github.io/portfolio/")))
        links_layout.addWidget(btn_portfolio)

        btn_github = QPushButton("💻 GitHub")
        btn_github.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                border: 1px solid {theme['border_color']};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {theme['hover_bg']}; }}
        """)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/angel-adel")))
        links_layout.addWidget(btn_github)

        layout.addLayout(links_layout)

        # Кнопка закрытия
        btn_close = QPushButton("Закрыть")
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['accent_color']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {theme['accent_hover']}; }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)