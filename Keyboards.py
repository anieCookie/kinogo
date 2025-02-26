from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


first_button_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Меню")]
], resize_keyboard=True, one_time_keyboard=True)


main_inlines_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Искать фильм по тегу #️⃣", callback_data="tag")],
    [InlineKeyboardButton(text="Искать фильм по описанию 📝", callback_data="movie")],
    [InlineKeyboardButton(text="Персональные рекомендации 🎯️", callback_data="recommend")],
    [InlineKeyboardButton(text="Моя статистика 📊", callback_data="stat")]
    ])



tags = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выбрать из библиотеки 📚", callback_data="lib")],
    [InlineKeyboardButton(text="Задать собственный тег 👨‍💻", callback_data="add_tag")]
])


lib = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Жанры ", callback_data="genre")],
    [InlineKeyboardButton(text="Теги ", callback_data="tags")]
    ])



recommend = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Получить рекомендации 🍿", callback_data="rec1")],
    [InlineKeyboardButton(text="Задать рекомендации ✍️", callback_data="rec2")],
    [InlineKeyboardButton(text="Сбросить рекомендации 🗑️", callback_data="rec3")]
])



