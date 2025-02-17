import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta

# Вставь сюда свой токен от BotFather
TOKEN = "7785269679:AAEWCaV5cMslIsqtev94OkzA9gZApKeKefI"

# Включаем логирование (чтобы видеть ошибки)
logging.basicConfig(level=logging.INFO)

# Создаём объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл для хранения задач
TASKS_FILE = "tasks.json"

def load_tasks():
    """Загружает задачи из JSON-файла"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tasks():
    """Сохраняет задачи в JSON-файл"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def clear_old_tasks():
    """Очищает задачи после 00:00"""
    global tasks
    current_date = datetime.now().strftime("%Y-%m-%d")
    if "date" not in tasks or tasks["date"] != current_date:
        tasks = {"date": current_date}
        save_tasks()

# Загружаем задачи
tasks = load_tasks()
clear_old_tasks()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я твой планер-бот. Какие задачи?")

@dp.message(Command("list"))
async def list_tasks(message: Message):
    """Выводит список задач"""
    user_id = str(message.from_user.id)

    if user_id not in tasks or not tasks[user_id]:
        await message.answer("📜 У тебя пока нет задач.")
        return

    task_list = "\n".join([f"{i+1}. {'✅' if task['done'] else '❌'} {task['task']}" for i, task in enumerate(tasks[user_id])])
    await message.answer(f"📋 Твои задачи:\n{task_list}")

@dp.message(Command("done"))
async def mark_done(message: Message):
    """Отмечает задачу как выполненную"""
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 2 or not args[1].isdigit():
        await message.answer("❌ Укажи номер задачи после /done. Пример: /done 2")
        return

    task_index = int(args[1]) - 1

    if user_id not in tasks or task_index < 0 or task_index >= len(tasks[user_id]):
        await message.answer("❌ Нет такой задачи. Проверь номер в списке /list.")
        return

    tasks[user_id][task_index]["done"] = True
    save_tasks()
    await message.answer(f"✅ Задача {task_index + 1} выполнена!")

@dp.message(Command("delete"))
async def delete_task(message: Message):
    """Удаление задачи по её номеру"""
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 2 or not args[1].isdigit():
        await message.answer("❌ Укажи номер задачи после команды /delete. Например: /delete 1")
        return

    task_index = int(args[1]) - 1

    if user_id not in tasks or task_index < 0 or task_index >= len(tasks[user_id]):
        await message.answer("❌ Задача с таким номером не найдена.")
        return

    deleted_task = tasks[user_id].pop(task_index)
    save_tasks()
    await message.answer(f"✅ Задача удалена: {deleted_task['task']}")

@dp.message(lambda message: message.text.startswith("/add"))
async def add_task(message: Message):
    """Добавление новой задачи"""
    user_id = str(message.from_user.id)
    task_text = message.text[len("/add "):].strip()

    if not task_text:
        await message.answer("❌ Пожалуйста, укажите текст задачи после команды /add.")
        return

    if user_id not in tasks:
        tasks[user_id] = []

    tasks[user_id].append({"task": task_text, "done": False})
    save_tasks()
    await message.answer(f"✅ Задача добавлена: {task_text}")

# Функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
