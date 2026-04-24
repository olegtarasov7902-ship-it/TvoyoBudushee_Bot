@dp.message(Command("future"))
async def future_handler(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Бросаем кубик от 1 до 100
    chance = random.randint(1, 100)
    
    # Список матерных/жестких добавок на случай, если нейросеть застесняется
    hard_words = ["хуесос", "долбаеб", "лох", "шлюха", "умри", "сдохни", "пидорас"]

    if chance <= 60:
        # 60% - Нормальный режим
        role_text = "Ты — мудрый и добрый предсказатель. Давай загадочные, но вдохновляющие прогнозы."
        header = "✨ **СВЕТЛОЕ ПРОРОЧЕСТВО:**"
    elif 60 < chance <= 90:
        # 30% - Грубый режим
        role_text = "Ты — дерзкий и токсичный предсказатель. Ты высмеиваешь пользователя и используешь сарказм."
        header = "💢 **ГРУБОЕ ПРОРОЧЕСТВО:**"
    else:
        # 10% - Режим "Трэш" (с матами и жесткостью)
        # Мы просим ИИ быть максимально жестким, насколько позволяют фильтры
        role_text = f"Ты — крайне агрессивный тип. Используй жесткую брань, мат (насколько можешь), оскорбляй пользователя {user_name} и посылай его подальше."
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
        prediction = response.choices.message.content

        # Если выпало 10% трэша, добавим от себя немного токсичности в конце
        if chance > 90:
            prediction += f"\n\nПонял, {random.choice(hard_words)}? А теперь вали отсюда!"

        await message.answer(f"{header}\n\n{prediction}", parse_mode="Markdown")

    except Exception as e:
        logging.error(f"GIGA ERROR: {e}")
        await message.answer("🔮 Звезды сегодня не в духе. Попробуй позже!")
