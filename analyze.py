from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from collections import defaultdict

CHAT_FILE = "messages.html"
YOUR_NAME = "Введи своё имя"  # <- поменяй на своё имя как оно написано в чате

PROGRESS_WORDS = ["сделал", "сделала", "запустил", "запустила", "работает", "починил", "починила", "готово", "получилось"]

DAYS_RU = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}


def load_messages(filename):
    with open(filename, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    messages = []
    for block in soup.find_all("div", class_="message default"):
        name_tag = block.find("div", class_="from_name")
        date_tag = block.find("div", class_="date")
        text_tag = block.find("div", class_="text")

        if not name_tag or not date_tag or not text_tag:
            continue

        date_str = date_tag.get("title", "")
        match = re.match(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", date_str)
        if not match:
            continue

        dt = datetime.strptime(match.group(1), "%d.%m.%Y %H:%M:%S")
        messages.append({
            "date": dt,
            "name": name_tag.get_text(strip=True),
            "text": text_tag.get_text(" ", strip=True),
        })

    return messages


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

    day_counts = defaultdict(int)
    for d in dates:
        day_counts[DAYS_RU[d.strftime("%A")]] += 1

    # Bug 2: переменная называется day_counts, но здесь написано days
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
        out.write("# Мой прогресс в интенсиве\n\n")
        out.write(f"**Участник:** {name}\n\n")
        out.write("| Метрика | Значение |\n")
        out.write("|---|---|\n")
        out.write(f"| Сообщений | {total} |\n")
        out.write(f"| Активный день | {busiest_day} |\n")
        out.write(f"| Прогресс-маркеры | {progress_count} |\n")
        out.write(f"| Вопросов | {questions} |\n")
        out.write(f"| Streak | {streak} 🔥 |\n")

    print("\n  Сохранено в my_progress.md")


if __name__ == "__main__":
    messages = load_messages(CHAT_FILE)
    analyze(messages, YOUR_NAME)
