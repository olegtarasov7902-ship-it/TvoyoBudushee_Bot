import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TG_TOKEN = "8735419644:AAE7rOpjsS4LCYOoyAPxgQt2oOuy2995YF8"
GIGA_KEY = "MDE5ZGJjOTQtMWVjNS03M2U3LThkMzYtMzI4NmRkN2VmNDYwOmE1MTQ4YWIzLTZlZjAtNDFkMS1hNzBhLTkyZmUxMTM1MmZmNA=="

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и нейросети
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
giga = GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False)

# --- МИКРО-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

# --- ЛОГИКА БОТА ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🔮 Я твой ИИ-пророк. Пиши /future, если не боишься узнать правду.")

@dp.message(Command("future"))
async def future_handler(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await bot.send_chat_action(message.chat.id, "typing")
    
    chance = random.randint(1, 100)
    hard_words = ["хуесос", "долбаеб", "пидорас", "сдохни", "лох", "умри"]

    if chance <= 60:
        role_text = "Ты — мудрый и добрый предсказатель. Давай загадочные, но вдохновляющие прогнозы."
        header = "✨ **СВЕТЛОЕ ПРОРОЧЕСТВО:**"
    elif 60 < chance <= 90:
        role_text = "Ты — дерзкий и токсичный предсказатель. Ты высмеиваешь пользователя и используешь сарказм."
        header = "💢 **ГРУБОЕ ПРОРОЧЕСТВО:**"
    else:
        role_text = f"Ты — крайне агрессивный тип. Используй жесткую брань, мат, оскорбляй пользователя {user_name} и посылай его."
        header = "🤬 **ЭКСТРЕМАЛЬНОЕ ПРОРОЧЕСТВО:**"

    try:
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=f"{role_text} Обращайся к {user_name}."),
                Messages(role=MessagesRole.USER, content=f"Напиши очень короткое предсказание для {user_name}.")
            ],
            model="GigaChat",
            max_tokens=200
        )
        response = giga.chat(payload)
        prediction = response.choices[0].message.content

        if chance > 90:
            prediction += f"\n\nСлышь, {random.choice(hard_words)}? А теперь вали!"

        await message.answer(f"{header}\n\n{prediction}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"GIGA ERROR: {e}")
        await message.answer("🔮 Звезды скрылись за тучами. Попробуй позже.")

async def main():
    print(">>> ЗАПУСК БОТА...")
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
