"""Темы оформления для Ádel Pilot"""

DARK_THEME = {
    "window_bg": "#1e1e2e",
    "text_color": "#cdd6f4",
    "border_color": "#313244",
    "accent_color": "#6a11cb",
    "accent_hover": "#7c22e0",
    "secondary_bg": "#181825",
    "secondary_text": "#a6adc8",
    "hover_bg": "#45475a",
    "button_bg": "#313244",
    "button_text": "#cdd6f4",
    "user_msg": "#89b4fa",
    "bot_msg": "#a6e3a1",
    "preview_bg": "#181825",
    "preview_text": "#6c7086",
    "link_color": "#89b4fa",
    "link_hover": "#b4befe",
    "code_bg": "#11111b",
    "code_text": "#cdd6f4",
}

LIGHT_THEME = {
    "window_bg": "#f5f5f7",
    "text_color": "#1e1e2e",
    "border_color": "#d1d1d6",
    "accent_color": "#6a11cb",
    "accent_hover": "#5a0fa8",
    "secondary_bg": "#ffffff",
    "secondary_text": "#6c7086",
    "hover_bg": "#e5e5ea",
    "button_bg": "#e5e5ea",
    "button_text": "#1e1e2e",
    "user_msg": "#0071e3",
    "bot_msg": "#2d8a4e",
    "preview_bg": "#ffffff",
    "preview_text": "#8e8e93",
    "link_color": "#0071e3",
    "link_hover": "#005bb5",
    "code_bg": "#f0f0f0",
    "code_text": "#1e1e2e",
}


def get_stylesheet(theme: dict) -> str:
    """Возвращает глобальный QSS для приложения"""
    return f"""
    QMainWindow {{ background-color: {theme['window_bg']}; color: {theme['text_color']}; }}
    QWidget {{ background-color: {theme['window_bg']}; color: {theme['text_color']}; }}
    QLineEdit {{
        background-color: {theme['secondary_bg']};
        color: {theme['text_color']};
        border: 1px solid {theme['border_color']};
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        selection-background-color: {theme['accent_color']};
    }}
    QListWidget {{
        background-color: {theme['secondary_bg']};
        color: {theme['text_color']};
        border: 1px solid {theme['border_color']};
        border-radius: 8px;
    }}
    QListWidget::item {{ padding: 8px; border-bottom: 1px solid {theme['border_color']}; }}
    QListWidget::item:selected {{ background-color: {theme['hover_bg']}; }}
    QListWidget::item:hover {{ background-color: {theme['hover_bg']}; }}
    QPushButton {{
        background-color: {theme['button_bg']};
        color: {theme['button_text']};
        border: 1px solid {theme['border_color']};
        border-radius: 6px;
        padding: 8px 15px;
        font-size: 13px;
    }}
    QPushButton:hover {{ background-color: {theme['hover_bg']}; }}
    QTextBrowser {{
        background-color: {theme['secondary_bg']};
        color: {theme['text_color']};
        border: 1px solid {theme['border_color']};
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }}
    QTextBrowser a {{ color: {theme['link_color']}; text-decoration: none; }}
    QTextBrowser a:hover {{ color: {theme['link_hover']}; text-decoration: underline; }}
    QLabel {{ color: {theme['text_color']}; }}
    QSplitter::handle {{ background-color: {theme['border_color']}; width: 2px; }}
    """