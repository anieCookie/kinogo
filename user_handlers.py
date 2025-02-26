from aiogram import Router, F
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from Keyboards import main_inlines_kb, lib, tags, recommend, first_button_kb
from ai_generators import generate
from aiogram.fsm.state import State, StatesGroup
from sentence_transformers import SentenceTransformer
import sqlite3
import os
import json
import numpy as np
from aiogram.utils.keyboard import InlineKeyboardBuilder

DB_PATH = "movies.db"
USER_PATH = "user.db"

q = " "

semantic_model = SentenceTransformer("sberbank-ai/sbert_large_nlu_ru")

user_router = Router()




async def set_processing(state: FSMContext, is_processing: bool):
    await state.update_data(is_processing=is_processing)

async def is_processing(state: FSMContext):
    data = await state.get_data()
    return data.get("is_processing", False)

class Work(StatesGroup):
    wait = State()
    process = State()
    mark = State()




#Старт
@user_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>!\nТы попал на бота команды <b>BackSpace</b> 🌌, я уверен, вам очень понравится)",
        reply_markup=first_button_kb, parse_mode='HTML')


@user_router.message(F.text == "Меню" or F.text == "/menu")
async def cmd_next(message: types.Message):
    await message.answer("Вот, что я умею ",
                         reply_markup=main_inlines_kb)




@user_router.callback_query(F.data == "lib")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Вот, что у меня есть",
                         reply_markup=lib)

@user_router.callback_query(F.data == "genre")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Вот, что у меня есть в этом разделе:")

@user_router.callback_query(F.data == "tags")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Вот, что у меня есть в этом разделе:")

@user_router.callback_query(F.data == "tag")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Введите тег, по которому вы хотите найти фильм",
                         reply_markup=tags)

@user_router.callback_query(F.data == "recommend")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Вот, что я могу вам предложить:",
                         reply_markup=recommend)






@user_router.callback_query(F.data == "movie")
async def cmd_search_movie(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Опиши фильм, который хочешь найти ")
    await state.set_state(Work.wait)


@user_router.callback_query(F.data == "add_tag")
async def cmd_search_movie(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Какой фильм Вас интересует? ")
    await state.set_state(Work.wait)




@user_router.callback_query(F.data == "rec1")
async def cmd_start_eda_callback(callback: types.CallbackQuery, state: FSMContext):
    kek = await callback.message.answer("Сейчас порекомендую фильмы, которые могут вам понравиться", reply_markup=main_inlines_kb)
    timer_message = await callback.message.answer("⏳")

    # Извлекаем предпочтения пользователя (если они есть)
    data = await state.get_data()
    user_query = data.get("q", "").strip()

    # Если предпочтений нет — сообщаем об этом
    if not user_query:
        await callback.message.answer("У вас пока нет сохранённых предпочтений. Расскажите, какие фильмы вам нравятся!",
                                      reply_markup=main_inlines_kb)
        await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=timer_message.message_id)
        await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=kek.message_id)
        return

    # Выполняем поиск
    results = description(user_query)

    # Формируем ответ
    if results:
        response = "\n\n".join([f"🎬 {title}\n⭐ {rating}\n📌 {genre}\n📖 {about}" for title, genre, year, about, rating in results])
    else:
        response = "Фильмы не найдены"

    # Отправляем ответ
    await callback.message.answer(response.encode("utf-16", "surrogatepass").decode("utf-16"))

    # Удаляем индикаторы загрузки
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=timer_message.message_id)
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=kek.message_id)

    # Завершаем состояние
    await state.clear()
    await callback.message.answer("<i>Если подборка не устраивает вас, уточните свои предпочтения или сбросьте их</i>",
                                  reply_markup=main_inlines_kb, parse_mode='HTML')


@user_router.callback_query(F.data == "rec2")
async def cmd_start_ai(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if "q" not in data:  # Проверяем, есть ли уже переменная q
        await state.update_data(q="")  # Создаём q, если её нет

    await callback.message.answer("Какие фильмы вам нравятся?")
    await state.set_state(Work.process)


@user_router.callback_query(F.data == "rec3")
async def cmd_start_eda_callback(callback: types.CallbackQuery, state: FSMContext):
    kek = await callback.message.answer("Подождите немного...", reply_markup=main_inlines_kb)
    timer_message = await callback.message.answer("⏳")

    await state.update_data(q=" ")

    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=timer_message.message_id)
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=kek.message_id)

    await callback.message.answer("<i>Рекомендации успешно сброшены</i>",
                                  reply_markup=main_inlines_kb, parse_mode='HTML')


def description(query):
    """
    Выполняет семантический поиск фильмов.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, rating, country, genre, year, duration, director, actors, tags, about, embedding_str1 FROM movies")
    rows = cursor.fetchall()
    conn.close()

    query_embedding = semantic_model.encode(query)
    results = []

    for title, rating, country, genre, year, duration, director, actors, tags, about, emb_str in rows:
        try:
            movie_embedding = np.array(json.loads(emb_str))
        except Exception:
            continue
        norm_q = np.linalg.norm(query_embedding)
        norm_m = np.linalg.norm(movie_embedding)

        similarity = np.dot(query_embedding, movie_embedding) / (norm_q * norm_m) if norm_q and norm_m else 0

        results.append((title, rating, country, genre, year, duration, director, actors, tags, about, similarity))

    results.sort(key=lambda x: x[10], reverse=True)
    return [(title, rating, country, genre, year, duration, director, actors, tags, about) for title, rating, country, genre, year, duration, director, actors, tags, about, _ in results[:3]]


def tag(query):
    """
        Выполняет семантический поиск фильмов.
        """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, rating, country, genre, year, duration, director, actors, tags, about, embedding_str2 FROM movies")
    rows = cursor.fetchall()
    conn.close()

    query_embedding = semantic_model.encode(query)
    results = []

    for title, rating, country, genre, year, duration, director, actors, tags, about, emb_str in rows:
        try:
            movie_embedding = np.array(json.loads(emb_str))
        except Exception:
            continue
        norm_q = np.linalg.norm(query_embedding)
        norm_m = np.linalg.norm(movie_embedding)

        similarity = np.dot(query_embedding, movie_embedding) / (norm_q * norm_m) if norm_q and norm_m else 0

        results.append((title, rating, country, genre, year, duration, director, actors, tags, about, similarity))

    results.sort(key=lambda x: x[10], reverse=True)
    return [(title, rating, country, genre, year, duration, director, actors, tags, about) for
            title, rating, country, genre, year, duration, director, actors, tags, about, _ in results[:3]]




@user_router.message(Work.wait)
async def process_movie(message: types.Message, state: FSMContext):
    query = message.text.strip()
    results = description(query)

    if not results or len(results) < 3:
        await message.answer("Фильмы не найдены")
        await state.clear()
        return

    # Фильм 1
    title1, rating1, country1, genre1, year1, duration1, director1, actors1, tags1, about1 = results[0]
    response1 = f"🎬 <b>{title1}</b>\n⭐ {rating1}\n📌 {genre1}\n📖 {about1}"
    keyboard1 = InlineKeyboardBuilder()
    keyboard1.button(text="➕ В рекомендации", callback_data="ar1")
    keyboard1.button(text="✅ Просмотрено", callback_data=f"w1")
    keyboard1.button(text="⭐ Оценить", callback_data="rate1")
    keyboard1.button(text="📽️ Подробнее о фильме", callback_data="info1")
    keyboard1.adjust(1)
    await message.answer(response1, parse_mode="HTML", reply_markup=keyboard1.as_markup())

    @user_router.callback_query(F.data == "ar1")
    async def cmd_start_ai(state: FSMContext):
        data = await state.get_data()
        if "q" not in data:
            await state.update_data(q="")

        data = await state.get_data()
        q = data.get("q", "") + ", " + tags1
        await state.update_data(q=q)
        await message.answer(
            "<i>Изменения успешно сохранены</i>",
            parse_mode='HTML'
        )

    @user_router.callback_query(F.data.startswith("rate1"))
    async def rate_callback(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(rating_title=title1)
        await callback.message.answer(f"Оцените фильм '{title1}' от 1 до 10")
        await state.set_state(Work.mark)

    @user_router.callback_query(F.data == "w1")
    async def mark_as_watched(callback: types.CallbackQuery):
        title = title1
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Обновляем значение столбца "watched" для выбранного фильма
        cursor.execute("UPDATE user SET watched = 1 WHERE title = ?", (title,))
        conn.commit()
        conn.close()

        await callback.message.answer(f"Фильм '{title}' помечен как просмотренный!")

    @user_router.callback_query(F.data == "info1")
    async def cmd_start_ai():
        response1 = f"🎬 <b>{title1}</b>\n⭐ {rating1}\n\n📌 {genre1}, {country1}, {year1} год\n\nℹ️ {duration1}\n\n🧑‍ {director1}\n🎭 {actors1}\n\n📖 {about1}"
        await message.answer(response1, parse_mode="HTML")

    # Фильм 2
    title2, rating2, country2, genre2, year2, duration2, director2, actors2, tags2, about2 = results[1]
    response2 = f"🎬 <b>{title2}</b>\n⭐ {rating2}\n📌 {genre2}\n📖 {about2}"
    keyboard2 = InlineKeyboardBuilder()
    keyboard2.button(text="➕ В рекомендации", callback_data=f"ar2")
    keyboard2.button(text="✅ Просмотрено", callback_data=f"w2")
    keyboard2.button(text="⭐ Оценить", callback_data=f"rate2")
    keyboard2.button(text="📽️ Подробнее о фильме", callback_data="info2")
    keyboard2.adjust(1)
    await message.answer(response2, parse_mode="HTML", reply_markup=keyboard2.as_markup())

    @user_router.callback_query(F.data == "ar2")
    async def cmd_start_ai(state: FSMContext):
        data = await state.get_data()
        if "q" not in data:
            await state.update_data(q="")

        data = await state.get_data()
        q = data.get("q", "") + ", " + tags2
        await state.update_data(q=q)
        await message.answer(
            "<i>Изменения успешно сохранены</i>",
            parse_mode='HTML'
        )

    @user_router.callback_query(F.data.startswith("rate2"))
    async def rate_callback(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(rating_title=title1)
        await callback.message.answer(f"Оцените фильм '{title2}' от 1 до 10")
        await state.set_state(Work.mark)

    @user_router.callback_query(F.data == "w2")
    async def mark_as_watched():
        title = title2
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Обновляем значение столбца "watched" для выбранного фильма
        cursor.execute("UPDATE user SET watched = 1 WHERE title = ?", (title,))
        conn.commit()
        conn.close()

        await message.answer(f"Фильм '{title}' помечен как просмотренный!")

    @user_router.callback_query(F.data == "info2")
    async def cmd_start_ai():
        response2 = f"🎬 <b>{title2}</b>\n⭐ {rating2}\n\n📌 {genre2}, {country2}, {year2} год\n\nℹ️ {duration2}\n\n🧑‍ {director2}\n🎭 {actors2}\n\n📖 {about2}"
        await message.answer(response2, parse_mode="HTML")

    # Фильм 3
    title3, rating3, country3, genre3, year3, duration3, director3, actors3, tags3, about3 = results[2]
    response3 = f"🎬 <b>{title3}</b>\n⭐ {rating3}\n📌 {genre3}\n📖 {about3}"
    keyboard3 = InlineKeyboardBuilder()
    keyboard3.button(text="➕ В рекомендации", callback_data=f"ar3")
    keyboard3.button(text="✅ Просмотрено", callback_data=f"w3")
    keyboard3.button(text="⭐ Оценить", callback_data=f"rate3")
    keyboard3.button(text="📽️ Подробнее о фильме", callback_data="info3")
    keyboard3.adjust(1)
    await message.answer(response3, parse_mode="HTML", reply_markup=keyboard3.as_markup())

    @user_router.callback_query(F.data == "ar3")
    async def cmd_start_ai(state: FSMContext):
        data = await state.get_data()
        if "q" not in data:
            await state.update_data(q="")

        data = await state.get_data()
        q = data.get("q", "") + ", " + tags3
        await state.update_data(q=q)
        await message.answer(
            "<i>Изменения успешно сохранены</i>",
            parse_mode='HTML'
        )

    @user_router.callback_query(F.data.startswith("rate3"))
    async def rate_callback(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(rating_title=title1)
        await callback.message.answer(f"Оцените фильм '{title3}' от 1 до 10")
        await state.set_state(Work.mark)

    @user_router.callback_query(F.data == "w3")
    async def mark_as_watched():
        title = title3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Обновляем значение столбца "watched" для выбранного фильма
        cursor.execute("UPDATE user SET watched = 1 WHERE title = ?", (title,))
        conn.commit()
        conn.close()

        await message.answer(f"Фильм '{title}' помечен как просмотренный!")

    @user_router.callback_query(F.data == "info3")
    async def cmd_start_ai():
        response3 = f"🎬 <b>{title3}</b>\n⭐ {rating3}\n\n📌 {genre3}, {country3}, {year3} год\n\nℹ️ {duration3}\n\n🧑‍ {director3}\n🎭 {actors3}\n\n📖 {about3}"
        await message.answer(response3, parse_mode="HTML")

    await state.clear()


@user_router.message(Work.mark)
async def save_rating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data.get("rating_title")

    try:
        rating = int(message.text)
        if 1 <= rating <= 10:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET mark = ? WHERE title = ?", (rating, title))
            conn.commit()
            conn.close()
            await message.answer(f"Вы поставили фильму '{title}' оценку {rating}/10")
        else:
            await message.answer("Введите число от 1 до 10")
            return
    except ValueError:
        await message.answer("Введите число от 1 до 10")
        return

    await state.clear()


@user_router.message(Work.process)
async def cmd_ai_process(message: types.Message, state: FSMContext):
    user_text = message.text.strip() if message.text else ""

    if not user_text:
        await message.answer("Пожалуйста, введите текст")
        return

    data = await state.get_data()
    q = data.get("q", "") + ", " + user_text
    await state.update_data(q=q)
    await message.answer(
        "<i>Изменения успешно сохранены</i>",
        reply_markup=main_inlines_kb,
        parse_mode='HTML'
    )
    await set_processing(state, False)




@user_router.message()
async def echo_messages(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    if message.text:
        await message.answer(text="Подождите...\nУ меня нет команды на данное сообщение.\nВот мой весь список команд:\n"                                  "/start - Запуск бота\n")
    else:
        try:
            await message.copy_to(chat_id=message.chat.id)
        except TypeError:
            await message.reply(text="💥🫣 Ничего непонятно...")
