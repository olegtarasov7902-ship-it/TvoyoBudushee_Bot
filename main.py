import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat

# --- КОНФИГУРАЦИЯ ---
# Рекомендую на Render использовать переменные окружения, но для начала вставь ключи сюда
TG_TOKEN = "8735419644:AAGEzP-E9273IBWKlx0NnlbeyqT3_BPzLkI"
GIGA_KEY = "ВАШ_GIGACHAT_KEY_MDE5Z..."

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
giga = GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🔮 Привет! Я ИИ-Оракул. Пиши /future, чтобы узнать судьбу.")

@dp.message(Command("future"))
async def future_handler(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await bot.send_chat_action(message.chat.id, "typing")

    # Логика 60/40 (нормальные / грубые ответы)
    chance = random.randint(1, 100)
    if chance <= 40:
        role = "Ты — дерзкий, токсичный тип. Можешь грубить, подкалывать и посылать пользователя."
        header = "💢 **Теневое пророчество:**"
    else:
        role = "Ты — мудрый, спокойный и добрый предсказатель."
        header = "✨ **Светлое пророчество:**"

    prompt = [
        {"role": "system", "content": f"{role} Обращайся к пользователю по имени {user_name}."},
        {"role": "user", "content": f"Напиши короткое и остроумное предсказание будущего для {user_name}."}
    ]

    try:
        response = giga.chat(prompt)
        # Получаем текст ответа
        prediction = response.choices[0].message.content
        await message.answer(f"{header}\n\n{prediction}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"GigaChat Error: {e}")
        await message.answer("🔮 Звезды сегодня не в духе. Попробуй позже!")

async def main():
    print(">>> БОТ УСПЕШНО ЗАПУЩЕН НА RENDER")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
