import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PySide6.QtCore import Qt

def generate_icons():
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    size = 512
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Градиент
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#6a11cb"))
    gradient.setColorAt(1, QColor("#2575fc"))
    
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    
    # Буква "Á" через Unicode (U+00C1)
    font = QFont("Segoe UI", 320, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    
    # Используем символ Á напрямую
    text_rect = painter.boundingRect(0, 0, size, size, Qt.AlignCenter, "\u00C1")
    text_rect.moveCenter(pixmap.rect().center())
    
    painter.drawText(text_rect, Qt.AlignCenter, "\u00C1")
    painter.end()
    
    # Сохраняем PNG
    png_path = os.path.join(assets_dir, "adel_pilot.png")
    pixmap.save(png_path)
    print(f"[Icons] Создано: {png_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    generate_icons()