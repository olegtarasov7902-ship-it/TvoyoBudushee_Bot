import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# --- КОНФИГУРАЦИЯ ---
# Твой новый токен
TG_TOKEN = "8735419644:AAE7rOpjsS4LCYOoyAPxgQt2oOuy2995YF8"
GIGA_KEY = "MDE5ZGJjOTQtMWVjNS03M2U3LThkMzYtMzI4NmRkN2VmNDYwOmM3OTEyYjk3LWJhMmYtNDkyZS04Njg4LTA5M2Q0YjY3NTE2ZQ=="

logging.basicConfig(level=logging.INFO)

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

    chance = random.randint(1, 100)
    if chance <= 40:
        role_text = "Ты — дерзкий, токсичный тип. Можешь грубить и посылать пользователя. Никакой вежливости."
        header = "💢 **Теневое пророчество:**"
    else:
        role_text = "Ты — мудрый и добрый предсказатель. Давай загадочные, но вдохновляющие прогнозы."
        header = "✨ **Светлое пророчество:**"

    try:
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=f"{role_text} Обращайся к пользователю {user_name}."),
                Messages(role=MessagesRole.USER, content=f"Напиши короткое предсказание будущего для {user_name}.")
            ],
            model="GigaChat",
            max_tokens=200
        )
        
        response = giga.chat(payload)
        prediction = response.choices[0].message.content # Исправили обращение к ответу
        
        await message.answer(f"{header}\n\n{prediction}", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"GigaChat Error: {e}")
        await message.answer("🔮 Звезды сегодня не в духе. Попробуй позже!")

async def main():
    print(">>> БОТ ЗАПУСКАЕТСЯ С НОВЫМ ТОКЕНОМ...")
    # Очищаем очередь старых сообщений, чтобы не было тормозов
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
