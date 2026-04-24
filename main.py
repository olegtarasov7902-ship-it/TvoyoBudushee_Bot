import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from aiohttp import web # Добавили это

# --- КОНФИГУРАЦИЯ ---
TG_TOKEN = "8735419644:AAE7rOpjsS4LCYOoyAPxgQt2oOuy2995YF8"
GIGA_KEY = "MDE5ZGJjOTQtMWVjNS03M2U3LThkMzYtMzI4NmRkN2VmNDYwOmE1MTQ4YWIzLTZlZjAtNDFkMS1hNzBhLTkyZmUxMTM1MmZmNA=="

logging.basicConfig(level=logging.INFO)
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
    site = web.TCPSite(runner, "0.0.0.0", 10000) # Render ищет порт здесь
    await site.start()
    print(">>> ВЕБ-СЕРВЕР ЗАПУЩЕН НА ПОРТУ 10000")

# --- ЛОГИКА БОТА ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🔮 Привет! Я твой личный ИИ-Оракул. Пиши /future!")

@dp.message(Command("future"))
async def future_handler(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await bot.send_chat_action(message.chat.id, "typing")
    
    chance = random.randint(1, 100)
    role_text = "Ты — дерзкий предсказатель." if chance <= 40 else "Ты — мудрый предсказатель."
    header = "💢 **ТЕНЬ:**" if chance <= 40 else "✨ **СВЕТ:**"

    try:
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=f"{role_text} Обращайся к {user_name}."),
                Messages(role=MessagesRole.USER, content="Напиши предсказание.")
            ],
            model="GigaChat",
            max_tokens=200
        )
        response = giga.chat(payload)
        await message.answer(f"{header}\n\n{response.choices[0].message.content}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"GIGA ERROR: {e}")
        await message.answer("🔮 Звезды скрылись...")

async def main():
    print(">>> ЗАПУСК БОТА...")
    # Запускаем веб-сервер в фоне
    await start_web_server()
    # Чистим обновления и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
