import asyncio
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
    await message.answer("🔮 Привет! Я бот-предсказатель. Отправь /future, чтобы заглянуть в будущее.")

@dp.message(Command("future"))
async def future_handler(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await bot.send_chat_action(message.chat.id, "typing")

    # Единый нейтральный стиль предсказания
    system_prompt = (
        f"Ты — нейтральный и точный предсказатель будущего. "
        f"Делай короткие, но интригующие прогнозы. Обращайся к {user_name} уважительно, "
        f"без оскорблений, сарказма и агрессии."
    )

    try:
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                Messages(role=MessagesRole.USER, content=f"Предскажи будущее для {user_name}.")
            ],
            model="GigaChat",
            max_tokens=200
        )
        response = giga.chat(payload)
        prediction = response.choices[0].message.content

        await message.answer(f"🔮 **Предсказание для тебя:**\n\n{prediction}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"GIGA ERROR: {e}")
        await message.answer("🔮 Звёзды сегодня неразговорчивы. Попробуй позже.")

async def main():
    print(">>> ЗАПУСК БОТА...")
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
