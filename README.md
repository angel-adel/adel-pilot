# 🤖 Ádel Pilot

<p align="center">
  <img src="https://img.shields.io/badge/version-0.001-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/UI-PySide6-green?style=for-the-badge&logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/LLM-Qwen2.5--1.5B-purple?style=for-the-badge" alt="LLM">
  <img src="https://img.shields.io/badge/platform-Windows-orange?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/license-By_Agreement-red?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>Умный десктопный ассистент с локальным ИИ для управления проектами, играми и файлами.</b><br>
  <i>Без облака. Без телеметрии. Без интернета. Только ты и твой компьютер.</i>
</p>

<p align="center">
  <img src="assets/adel_pilot.png" width="200" alt="Ádel Pilot Logo">
</p>

---

## ✨ Возможности

### 🧠 Интеллектуальный чат
- Понимает запросы на естественном языке: *"открой S-Connect"*, *"запусти Derail Valley"*
- Предлагает **кнопки-действия** вместо угадывания: Папка / VS Code / Android Studio / Запустить
- Автоматически находит `.exe` внутри папок портативных приложений

### 🔍 Двухпанельный интерфейс
- **Левая панель** — чат с ИИ и кнопками
- **Правая панель** — мгновенный поиск по базе с превью:
  - 🖼️ Картинки отображаются целиком
  - 📄 Код и текст — с подсветкой
  - 📁 Папки — с количеством файлов внутри

### 🎨 Темы оформления
- 🌙 Тёмная тема (Catppuccin Mocha)
- ☀️ Светлая тема
- Выбор сохраняется между запусками

### 🔒 Безопасность
- Чёрный список системных папок (`Windows`, `System32`, `Program Files`, реестр)
- Проверка каждого пути перед выполнением действия
- Защита от "галлюцинаций" ИИ: путь должен реально существовать в базе

### 🚀 Лаунчер
- Плавающая кнопка «Á» с перетаскиванием по экрану
- Иконка в системном трее с контекстным меню
- Двойной клик по кнопке — выход из программы

### 📂 Автопоиск
- Сканирует все диски (C:, D:, E:...) в поисках папок `Games`, `Projects`, `Игры`, `Проекты`
- Индексирует сохранения игр из `AppData\Local`
- Работает на любом ПК без настройки путей

---

## 📸 Скриншоты

<p align="center">
  <img src="assets/screenshot.png" alt="Интерфейс Ádel Pilot" width="800">
</p>

---

## 🧠 О модели ИИ

В Ádel Pilot используется **Qwen2.5-1.5B-Instruct** в квантовании `Q4_K_M`:

| Параметр | Значение |
|----------|----------|
| Размер модели | ~900 МБ |
| Контекст | 2048 токенов |
| Потоков CPU | 4 |
| Формат | GGUF (llama.cpp) |
| Запуск | Полностью локальный |

**Почему именно она:**
- Достаточно умна для структурированного JSON-ответа
- Работает на любом современном CPU без видеокарты
- Не требует интернета и аккаунтов
- Открытая лицензия (Apache 2.0)

---

## 🚀 Установка

### Для пользователей
1. Скачай архив `AdelPilot.zip` из раздела [Releases](../../releases)
2. Распакуй в любое удобное место (например, `C:\Tools\AdelPilot\`)
3. Запусти `AdelPilot.exe`
4. При первом запуске программа проиндексирует файлы (1-2 минуты)

### Для разработчиков
```bash
git clone https://github.com/angel-adel/adel-pilot.git
cd adel-pilot
pip install -r requirements.txt
python icons.py          # генерация иконок
python run_index.py      # первичная индексация
python main.py           # запуск
