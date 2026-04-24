import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# --- КОНФИГУРАЦИЯ ---
# Твой актуальный токен
TG_TOKEN = "8735419644:AAE7rOpjsS4LCYOoyAPxgQt2oOuy2995YF8"
# Твой актуальный ключ GigaChat
GIGA_KEY = "MDE5ZGJjOTQtMWVjNS03M2U3LThkMzYtMzI4NmRkN2VmNDYwOmE1MTQ4YWIzLTZlZjAtNDFkMS1hNzBhLTkyZmUxMTM1MmZmNA=="

# Настройка логирования для Render (чтобы видеть ошибки в логах)
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
giga = GigaChat(credentials=GIGA_KEY, verify_ssl_certs=False)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🔮 Привет! Я твой личный ИИ-Оракул.\n\nНапиши /future, и я загляну в бездну твоего будущего...")

@dp.message(Command("future"))
async def future_handler(message: types.Message):
    # Получаем ник или имя
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    # Визуальный эффект "печатает"
    await bot.send_chat_action(message.chat.id, "typing")

    # Шанс 40/60 на грубый или нормальный ответ
    chance = random.randint(1, 100)
    if chance <= 40:
        role_text = "Ты — дерзкий, токсичный и очень грубый предсказатель. Ты высмеиваешь пользователя и можешь его послать. Используй сарказм."
        header = "💢 **МРАЧНОЕ ПРОРОЧЕСТВО:**"
    else:
        role_text = "Ты — мудрый, добрый и загадочный предсказатель. Давай вдохновляющие и интересные советы."
        header = "✨ **СВЕТЛОЕ ПРОРОЧЕСТВО:**"

    try:
        # Формируем запрос к GigaChat по новому стандарту
        payload = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=f"{role_text} Обращайся к пользователю {user_name}."),
                Messages(role=MessagesRole.USER, content=f"Предскажи будущее для пользователя {user_name}. Будь краток и остроумен.")
            ],
            model="GigaChat",
            max_tokens=300
        )
        
        response = giga.chat(payload)
        prediction = response.choices[0].message.content
        
        # Отправляем результат пользователю
        await message.answer(f"{header}\n\n{prediction}", parse_mode="Markdown")

    except Exception as e:
        # Если что-то пойдет не так, мы увидим это в логах Render
        logging.error(f"GIGA ERROR: {e}")
        await message.answer("🔮 Звезды сегодня затуманились... Видимо, твоя судьба слишком мощная для моих алгоритмов. Попробуй еще раз позже!")

async def main():
    print(">>> БОТ ОЖИВАЕТ И ВЫХОДИТ НА СВЯЗЬ...")
    # Удаляем старые сообщения, которые бот пропустил, пока был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    # Запуск
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(">>> БОТ ВЫКЛЮЧЕН")
