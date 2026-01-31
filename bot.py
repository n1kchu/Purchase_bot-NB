from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8414386437:AAHcoUuHl6dEofnmS_jSkP8G8GiqlO4-PVo"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== ДАННЫЕ =====
categories = {
    "Vodka": ["Кабарга", "Бульбаш", "Absolut"],
    "Whiskey": ["Red Label", "Jameson", "Chivas Regal 12 Y.O", "Jim Beam Boubon",
                "Jim Beam Honey", "Jim Beam Apple", "Jim Beam Black Cherry"],
    "Rum": ["Captain Morgan White", "Captain Morgan Dark", "Captain Morgan Spiced", "Oakheart"],
    "Gin": ["Gordon's London Dry", "Gordon's Premium Pink"],
    "Tequila": ["Olmeca Silver", "Olmeca Gold"],
    "Cognac": ["Courvousier VS", "GalaVani 5*", "Казахстан 3*", "Казахстан 5*"],
    "Vermouth": ["Martini Bianco", "Martini Fiero", "Martini Rosso", "Martini Extra Dry"],
    "Liquor": ["Jagermeister", "Absinthe", "Malibe", "Kahlua", "Baileys",
               "Sambuca", "Cointrau", "Aperol", "Amaretto"],
    "Infusion": ["Doctor August"],
    "Still Wines ": ["Kindzmarauli", "Alazani Valley White", "Alazani Valley Red",
                            "Saperavi", "Cinandali", "Charton Blan", "Charton Rouge",
                            "Alore Vino Pinot Grigio", "Alore Vino Sagiovee", "Casiliero Del Diablo Chardonnay", "Barefoot White"],
    "Sparkling Wines": ["Lambrusco Bianco", "Lambrusco Rosso", "Lambrusco Rosato", "Martini Asi"],
    "Bottle Beer": ["Corona Extra", "Miller", "Bavaria", "Efes", "Kronenburg Blanc 1664", "Carlsberg 0%"],
    "Draft Beer": ["Легенда 10", "Holsten"],
    "Soft Drinks": ["Сок вишня", "Сок персик", "Сок яблоко", "Сок апельсин", "Сок гранат",
                    "Сок ананас", "Сок тропик", "Pepsi 0,5L", "Pepsi 0,25L", "7Up 0,5L",
                    "7Up 0,25L", "Schweppes", "Red Bull", "Asu б/г", "Asu газ.", "Borjomi"],
    "Additional Products": ["Parliament", "LM", "Neo", "Neo Slim", "Зажигалки", "Жвачки"],
    "Snacks": ["Арахис", "Фисташки", "Чечил", "Чипсы", "Крутики", "Лимон", "Лайм", "Апельсин"],
    "Хаус": ["Tassay energy", "Хаома", "Blue Curacao", "Propeller Whiskey", "Sierra Blanco",
             "Газ вода 1,5л", "Pepsi 1L", "7Up 1L", "Советское", "Сахар", "Лимонка"],
    "Сиропы": ["Зеленая дыня", "Гренадин", "Малина", "Клубника", "Киви", "Манго", "Маракуйя"]
}

cart = {}  # user_id -> {item: count}

# ===== КЛАВИАТУРЫ =====
def main_menu_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat in categories:
        kb.add(types.InlineKeyboardButton(cat, callback_data=f"cat:{cat}"))
    kb.add(types.InlineKeyboardButton("📋 Сформировать закуп", callback_data="checkout"))
    return kb

def items_keyboard(category, user_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for item in categories[category]:
        count = cart.get(user_id, {}).get(item, 0)
        kb.add(
            types.InlineKeyboardButton(f"➕ {item} ({count})", callback_data=f"add:{category}:{item}"),
            types.InlineKeyboardButton(f"➖ {item} ({count})", callback_data=f"sub:{category}:{item}")
        )
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return kb

# ===== ХЕНДЛЕРЫ =====
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Главное меню. Выбери категорию или сформируй закуп:",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data.startswith("cat:"))
async def open_category(callback: types.CallbackQuery):
    category = callback.data.split(":")[1]
    user_id = callback.from_user.id
    await callback.message.edit_text(
        f"Категория: {category}\nНажимай ➕ или ➖ для изменения количества:",
        reply_markup=items_keyboard(category, user_id)
    )

@dp.callback_query_handler(lambda c: c.data.startswith("add:"))
async def add_item(callback: types.CallbackQuery):
    _, category, item = callback.data.split(":")
    user_id = callback.from_user.id
    if user_id not in cart:
        cart[user_id] = {}
    cart[user_id][item] = cart[user_id].get(item, 0) + 1
    await callback.message.edit_reply_markup(reply_markup=items_keyboard(category, user_id))
    await callback.answer(f"{item}: {cart[user_id][item]}")

@dp.callback_query_handler(lambda c: c.data.startswith("sub:"))
async def sub_item(callback: types.CallbackQuery):
    _, category, item = callback.data.split(":")
    user_id = callback.from_user.id
    if user_id not in cart:
        cart[user_id] = {}
    if cart[user_id].get(item, 0) > 0:
        cart[user_id][item] -= 1
    await callback.message.edit_reply_markup(reply_markup=items_keyboard(category, user_id))
    await callback.answer(f"{item}: {cart[user_id].get(item,0)}")

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню. Выбери категорию или сформируй закуп:",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in cart or not any(cart[user_id].values()):
        await callback.message.answer("Корзина пустая")
    else:
        text = "🛒 Закуп:\n\n"
        # Формируем текст по категориям
        for cat, items in categories.items():
            cat_items = []
            for item in items:
                count = cart[user_id].get(item, 0)
                if count > 0:
                    cat_items.append(f"  - {item} — {count}")
            if cat_items:
                text += f"{cat}:\n" + "\n".join(cat_items) + "\n\n"
        await callback.message.answer(text.strip())
        cart[user_id] = {}  # обнуляем корзину
    await callback.message.edit_text(
        "Главное меню. Выбери категорию или сформируй закуп:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer("Закуп сформирован и корзина очищена!")

# ===== СТАРТ БОТА =====
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
