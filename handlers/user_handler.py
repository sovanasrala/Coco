from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from config_data.config import Config, load_config
from keyboards.user_keyboard import main_menu, keyboards_get_phone, keyboards_manager_link, keyboards_chanel_link, \
    keyboards_back_main_menu
from module.data_base import create_table_users, add_user

import requests
import logging


router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()


@router.message(CommandStart())
async def process_start_command_user(message: Message) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    create_table_users()
    add_user(id_user=message.chat.id, user_name=message.from_user.username)
    await message.answer(
        text=f"🙍<b>{message.from_user.first_name}</b> Добро пожаловать! Я помогу вам, с чего начнем?🏮",
        reply_markup=main_menu(),
        parse_mode='html')


@router.message(F.text == "Заказать уголь 💷")
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer(text="💬Введите ваше имя:")


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer(text="💬Введите ваш возраст:")


@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.number)
    await message.answer(text="💬Отправьте ваш номер телефона:",
                         reply_markup=keyboards_get_phone())


@router.message(Register.number, F.contact)
async def register_number(message: Message, state: FSMContext):
    await state.update_data(number=message.contact.phone_number)
    user_dict[message.chat.id] = await state.get_data()
    await message.answer(text=f'📚Ваше имя: {user_dict[message.chat.id]["name"]}\n'
                              f'Ваш возраст: {user_dict[message.chat.id]["age"]}\n'
                              f'Номер: {user_dict[message.chat.id]["number"]}')
    await state.clear()


@router.message(F.text == "Техподдержка ☎️")
async def links(message: Message):
    await message.answer(text="✊🏻Вот c нашим менеджером:",
                         reply_markup=keyboards_manager_link())


@router.message(F.text == "Наш канал 🧧")
async def links_channel(message: Message):
    logging.info("links_channel")
    await message.answer(f"Подпишись на наш телеграм канал:", reply_markup=keyboards_chanel_link())


@router.message(F.text == "О нас❓")
async def links_about(message: Message):
    logging.info("links_about")
    await message.answer(text=f"Coco-coal:\n"
                              f"👉🏻Это не просто уголь, а качественный продукт наравне с такими известными брендами, как Краун и Коколоко. \n"
                              f"👉🏻Мы долго работали проектом, стремясь создать что-то по-настоящему уникальное.\n"
                              f"👉🏻Уголь наивысшей категории, собранный на острове в Тихом океане. Сделан из натуральных продуктов, а именно, из лучших сортов кокосовой скорлупы.\n"
                              f"👉🏻Идеальная увеличенная форма куба позволяет обеспечить долгое горение, а состав органически выверен, что позволяет насладиться кальяном и его вкусом без лишних примесей и запахов.\n",
                         reply_markup=keyboards_back_main_menu())


@router.callback_query(F.data == "main_menu")
async def links_about(callback: CallbackQuery):
    logging.info("links_about")
    await callback.message.answer(text=f"🙍<b>{callback.from_user.first_name}</b> Добро пожаловать! Я помогу вам, с чего начнем?🏮",
                                  reply_markup=main_menu(),
                                  parse_mode='html')