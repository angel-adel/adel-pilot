import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import QObject, Signal
import config


class TrayController(QObject):
    request_search = Signal()
    request_quit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon()

        # Надёжная загрузка иконки через QPixmap (PNG работает лучше, чем ICO)
        if os.path.isfile(config.TRAY_ICON):
            pixmap = QPixmap(config.TRAY_ICON)
            if not pixmap.isNull():
                self.tray.setIcon(QIcon(pixmap))
                print(f"[Tray] Иконка загружена: {config.TRAY_ICON}", flush=True)
            else:
                print(f"[Tray] Файл найден, но не является изображением: {config.TRAY_ICON}", flush=True)
                self.tray.setIcon(QIcon())
        else:
            print(f"[Tray] Иконка НЕ найдена по пути: {config.TRAY_ICON}", flush=True)
            self.tray.setIcon(QIcon())

        self.tray.setToolTip(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.tray.activated.connect(self._on_activated)

        # Контекстное меню
        self.menu = QMenu()

        act_show = QAction(f"Открыть {config.APP_NAME}", self.menu)
        act_show.triggered.connect(self.request_search.emit)
        self.menu.addAction(act_show)

        self.menu.addSeparator()

        act_quit = QAction("Завершить работу", self.menu)
        act_quit.triggered.connect(self.request_quit.emit)
        self.menu.addAction(act_quit)

        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def _on_activated(self, reason):
        # Одиночный клик по иконке в трее — открыть окно
        if reason == QSystemTrayIcon.Trigger:
            self.request_search.emit()