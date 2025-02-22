from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


first_button_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Меню")]
], resize_keyboard=True, one_time_keyboard=True)

#МЕНЮ..............................................................................
main_inlines_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Искать фильм по тегу #️⃣", callback_data="tag")],
    [InlineKeyboardButton(text="Искать фильм по описанию 📝", callback_data="movie")],
    [InlineKeyboardButton(text="Персональные рекомендации 💁‍♂️", callback_data="recommend",)],
    ])


#теги////////////////////////////////////////////////////////////////////////////////////////
tags = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выбрать из библиотеки 📚", callback_data="lib")],
    [InlineKeyboardButton(text="Задать собственный тег 👨‍💻", callback_data="add_tag")]
])

#библиотека//////////////////////////////////////////////////////////////////////////////////
lib = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="А.. - Д.. ", callback_data="b")],
    [InlineKeyboardButton(text="Е.. - Р.. ", callback_data="k")],
    [InlineKeyboardButton(text="С.. - Я.. ", callback_data="f")],
    ])


b = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Биография ", callback_data="bio")],
    [InlineKeyboardButton(text="Боевик ", callback_data="boevik")],
    [InlineKeyboardButton(text="Вестерн ", callback_data="west")],
    [InlineKeyboardButton(text="Детектив ", callback_data="detective")],
    [InlineKeyboardButton(text="Драма ", callback_data="drama")]
    ])

k = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Комедия ", callback_data="comedy")],
    [InlineKeyboardButton(text="Мелодрама ", callback_data="movie")],
    [InlineKeyboardButton(text="Мистика ", callback_data="mistic")],
    [InlineKeyboardButton(text="Приключение ", callback_data="adventure")],
    [InlineKeyboardButton(text="Ромком ", callback_data="romcom")]
    ])

f = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Трагикомедия ", callback_data="tragedy")],
    [InlineKeyboardButton(text="Триллер ", callback_data="triller")],
    [InlineKeyboardButton(text="Ужасы ", callback_data="horror")],
    [InlineKeyboardButton(text="Фантастика ", callback_data="fantastic")],
    [InlineKeyboardButton(text="Фэнтези ", callback_data="fantasy")]
    ])

#реки////////////////////////////////////////////////////////////////////////////////////////
recommend = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Получить рекомендации 📊", callback_data="rec1")],
    [InlineKeyboardButton(text="Задать рекомендации ✍️", callback_data="rec2")],
    [InlineKeyboardButton(text="Сбросить рекомендации 🗑️", callback_data="rec3")]
])



lol_button_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Начать новый диалог")],
    [KeyboardButton(text="Вернуться в меню")]
], resize_keyboard=True, one_time_keyboard=True)