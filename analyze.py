import re
from datetime import datetime, timedelta
from collections import defaultdict

CHAT_FILE = "chat.html"  # Bug 1: неправильное имя файла
YOUR_NAME = "Введи своё имя"  # <- поменяй на своё имя как оно написано в чате

PROGRESS_WORDS = ["сделал", "сделала", "запустил", "запустила", "работает", "починил", "починила", "готово", "получилось"]


def load_messages(filename):
    messages = []
    # Bug 1: открываем файл без указания кодировки
    with open(filename) as f:
        html = f.read()

    # Находим все блоки сообщений
    blocks = re.findall(
        r'class="from_name">\s*(.+?)\s*</div>.*?'
        r'title="(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})[^"]*".*?'
        r'class="text">\s*(.*?)\s*</div>',
        html, re.DOTALL
    )

    for name, date_str, text in blocks:
        dt = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        # Убираем HTML-теги из текста
        clean_text = re.sub(r'<[^>]+>', ' ', text).strip()
        messages.append({"date": dt, "name": name.strip(), "text": clean_text})

    return messages


DAYS_RU = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}


def calculate_streak(dates):
    if not dates:
        return 0
    unique_days = sorted(set(d.date() for d in dates))
    streak = 1
    for i in range(1, len(unique_days)):
        if unique_days[i] - unique_days[i - 1] == timedelta(days=1):
            streak += 1
        else:
            streak = 1
    return streak


def analyze(messages, name):
    my_messages = [m for m in messages if name.lower() in m["name"].lower()]

    if not my_messages:
        print(f"Участник '{name}' не найден в чате. Проверь имя в переменной YOUR_NAME.")
        return

    total = len(my_messages)
    dates = [m["date"] for m in my_messages]
    days = defaultdict(int)
    for d in dates:
        # Bug 2: используем английское название дня вместо русского
        days[d.strftime("%A")] += 1

    busiest_day = max(days, key=days.get)
    progress_count = sum(1 for m in my_messages if any(w in m["text"].lower() for w in PROGRESS_WORDS))
    questions = sum(1 for m in my_messages if "?" in m["text"])
    streak = calculate_streak(dates)

    print("─" * 40)
    print(f"  Участник: {name}")
    print("─" * 40)
    print(f"  Сообщений написано:       {total}")
    print(f"  Самый активный день:      {busiest_day}")
    print(f"  Прогресс-маркеры:         {progress_count}")
    print(f"  Вопросов задано:          {questions}")
    print(f"  Streak (дней подряд):     {streak} 🔥")
    print("─" * 40)

    with open("my_progress.md", "w", encoding="utf-8") as out:
        out.write(f"# Мой прогресс в интенсиве\n\n")
        out.write(f"**Участник:** {name}\n\n")
        out.write(f"| Метрика | Значение |\n")
        out.write(f"|---|---|\n")
        out.write(f"| Сообщений | {total} |\n")
        out.write(f"| Активный день | {busiest_day} |\n")
        out.write(f"| Прогресс-маркеры | {progress_count} |\n")
        out.write(f"| Вопросов | {questions} |\n")
        out.write(f"| Streak | {streak} 🔥 |\n")

    print("\n  Сохранено в my_progress.md")


if __name__ == "__main__":
    messages = load_messages(CHAT_FILE)
    analyze(messages, YOUR_NAME)
