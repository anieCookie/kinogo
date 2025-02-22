from aiogram import Router, F
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from Keyboards import main_inlines_kb, lib, tags, b, k, f, recommend, first_button_kb, lol_button_kb
from ai_generators import generate
from aiogram.fsm.state import State, StatesGroup
from context import ContexManager
from sentence_transformers import SentenceTransformer
import sqlite3
import os
import json
import numpy as np

DB_PATH = "movies.db"
q = " "
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

context = ContexManager()
user_router = Router()



#Храним состояние генерации в FSM контексте
async def set_processing(state: FSMContext, is_processing: bool):
    await state.update_data(is_processing=is_processing)

async def is_processing(state: FSMContext):
    data = await state.get_data()
    return data.get("is_processing", False)

class Work(StatesGroup):
    wait = State()
    process = State()



#База
@user_router.message(F.text == "Начать новый диалог")
async def clear1(message: types.Message):
    context.contex = {}
    await message.answer(text="История очищена")


#Старт
@user_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>!\nТы попал на бота команды <b>BackSpace</b> 🌌, я уверен, вам очень понравится)",
        reply_markup=first_button_kb, parse_mode='HTML')


@user_router.message(F.text == "Меню")
async def cmd_next(message: types.Message):
    await message.answer("Вот, что я умею ",
                         reply_markup=main_inlines_kb)


@user_router.message(F.text == "Вернуться в меню")
async def cmd_next(message: types.Message):
    await message.answer("Вот, что я знаю о Екатеринбурге ",
                         reply_markup=main_inlines_kb)


@user_router.callback_query(F.data == "lib")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
                         reply_markup=lib)

@user_router.callback_query(F.data == "b")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
                         reply_markup=b)

@user_router.callback_query(F.data == "k")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
                         reply_markup=k)

@user_router.callback_query(F.data == "f")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
                         reply_markup=f)

@user_router.callback_query(F.data == "tag")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
                         reply_markup=tags)

@user_router.callback_query(F.data == "recommend")
async def cmd_zanatie(callback: types.CallbackQuery):
    await callback.message.answer("Что вас интересует?",
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
    kek = await callback.message.answer("Сейчас порекомендую фильмы, которые могут понравиться вам", reply_markup=lol_button_kb)
    timer_message = await callback.message.answer("⏳")
    await state.set_state(Work.process)
    await process_movie(q)
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=timer_message.message_id)
    await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=kek.message_id)
    await state.clear()
    await callback.message.answer("<i>Если подборка не устраивает вас, можете уточнить свои предпочтения"
                                  " или полностью сбросить их</i>",
                                  reply_markup=main_inlines_kb, parse_mode='HTML')


@user_router.callback_query(F.data == "rec2")
async def cmd_start_ai(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if "q" not in data:  # Проверяем, есть ли уже переменная q
        await state.update_data(q="")  # Создаём q, если её нет

    await callback.message.answer("Какие фильмы вам нравятся?")
    await state.set_state(Work.process)


@user_router.callback_query(F.data == "rec3")
async def cmd_start_eda_callback(callback: types.CallbackQuery, q: q):
    kek = await callback.message.answer("Подождите немного...", reply_markup=lol_button_kb)
    timer_message = await callback.message.answer("⏳")
    q = " "

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
    cursor.execute("SELECT title, rating, embedding_str FROM movies")
    rows = cursor.fetchall()
    conn.close()

    query_embedding = semantic_model.encode(query)
    results = []

    for title, rating, emb_str in rows:
        try:
            movie_embedding = np.array(json.loads(emb_str))
        except Exception:
            continue
        norm_q = np.linalg.norm(query_embedding)
        norm_m = np.linalg.norm(movie_embedding)
        similarity = np.dot(query_embedding, movie_embedding) / (norm_q * norm_m) if norm_q and norm_m else 0
        results.append((title, rating, similarity))

    results.sort(key=lambda x: x[2], reverse=True)
    return [(title, rating) for title, rating, _ in results[:3]]

def tag(query):
    """
    Выполняет семантический поиск фильмов по жанру.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, rating, genre FROM movies")
    rows = cursor.fetchall()
    conn.close()

    query_embedding = semantic_model.encode(query)
    results = []

    for title, rating, genre in rows:
        genre_embedding = semantic_model.encode(genre)
        norm_q = np.linalg.norm(query_embedding)
        norm_g = np.linalg.norm(genre_embedding)
        similarity = np.dot(query_embedding, genre_embedding) / (norm_q * norm_g) if norm_q and norm_g else 0
        results.append((title, rating, similarity))

    results.sort(key=lambda x: x[2], reverse=True)
    return [(title, rating) for title, rating, _ in results[:3]]

@user_router.message(Work.wait)
async def process_movie(message: types.Message, state: FSMContext):
    query = message.text.strip()
    results = description(query)
    response = "\n\n".join([f"\ud83c\udfae {title}\n⭐ {rating}" for title, rating in results]) if results else "Фильмы не найдены"
    response = response.encode("utf-16", "surrogatepass").decode("utf-16")
    await message.answer(response)
    await state.clear()




@user_router.message(Work.process)
async def cmd_ai_process(message: types.Message, state: FSMContext):
    user_text = message.text.strip() if message.text else ""

    if not user_text:
        await message.answer("Пожалуйста, введите текст.")
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