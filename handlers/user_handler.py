from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state

from config_data.config import Config, load_config
from keyboards.user_keyboard import main_menu, keyboards_get_phone, keyboards_manager_link, keyboards_chanel_link, \
    keyboards_back_main_menu, keyboards_confirm_register
from module.data_base import create_table_users, add_user

import requests
import logging
import re

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class Register(StatesGroup):
    count = State()
    name = State()
    number = State()
    address = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    print(response.json())
    return response.json()


def validate_russian_phone_number(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)


@router.message(CommandStart())
async def process_start_command_user(message: Message) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    create_table_users()
    add_user(id_user=message.chat.id,
             user_name=message.from_user.username)
    await message.answer(
        text=f"🙍<b>{message.from_user.first_name}</b> Добро пожаловать! Я помогу вам, с чего начнем?🏮",
        reply_markup=main_menu(),
        parse_mode='html')


@router.message(F.text == "Заказать уголь 💷")
async def register(message: Message, state: FSMContext):
    logging.info(f'register: {message.chat.id}')
    await state.set_state(Register.name)
    await message.answer(text="💬 Какое количество кг угля вас интересует?",
                         reply_markup=keyboards_back_main_menu())
    await state.set_state(Register.count)


@router.message(Register.count, lambda message: message.text.isdigit())
async def register_count(message: Message, state: FSMContext):
    logging.info(f'register_count: {message.chat.id}')
    await state.update_data(count=message.text)
    await state.set_state(Register.number)
    await message.answer(text="💬Отправьте ваш номер телефона:",
                         reply_markup=keyboards_get_phone())


@router.message(Register.count)
async def register_count_error(message: Message):
    logging.info(f'register_count_error: {message.chat.id}')
    await message.answer(text="💬Кажется вы ошиблись при вводе количества. Попробуйте еще раз, но только цифрами."
                              " Например: 1, 20, 40, 4000",
                         reply_markup=keyboards_back_main_menu())


@router.message(Register.number)
async def register_number(message: Message, state: FSMContext):
    logging.info(f'register_number: {message.chat.id}')
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера. Повторите ввод:")
            return
    await state.update_data(phone=phone)
    await state.set_state(Register.name)
    await message.answer(text="💬 Укажите ваше имя:",
                         reply_markup=keyboards_back_main_menu())


@router.message(Register.name, lambda message: len(message.text) < 255)
async def register_name(message: Message, state: FSMContext):
    logging.info(f'register_name: {message.chat.id}')
    await state.update_data(name=message.text)
    await state.set_state(Register.address)
    await message.answer(text="💬Отправьте ваш адрес:",
                         reply_markup=keyboards_back_main_menu())


@router.message(Register.name)
async def register_name_error(message: Message):
    logging.info(f'register_name_error: {message.chat.id}')
    await message.answer(text="💬Кажется вы отправили более 255 символов. Пожалуйста повторите ввод имени")


@router.message(Register.address, lambda message: len(message.text) < 4096)
async def register_address(message: Message, state: FSMContext, bot: Bot):
    logging.info(f'register_address: {message.chat.id}')
    await state.update_data(address=message.text)
    user_dict[message.chat.id] = await state.get_data()
    await message.answer(text=f'📚Ваше имя: {user_dict[message.chat.id]["name"]}\n'
                              f'Ваш адрес: {user_dict[message.chat.id]["address"]}\n'
                              f'Номер телефона: {user_dict[message.chat.id]["phone"]}\n'
                              f'Количество угля: {user_dict[message.chat.id]["count"]} кг',
                         reply_markup=keyboards_confirm_register())
    await state.set_state(default_state)


@router.callback_query(F.data == "confirm_register")
async def links_about(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info("links_about")
    await callback.message.answer(text='Скоро с вами свяжется оператор',
                                  reply_markup=main_menu())
    await callback.message.answer(text='А пока предлагаю, посмотреть наш телеграм канал, там много интересного',
                                  reply_markup=keyboards_manager_link())
    user_dict[callback.message.chat.id] = await state.get_data()
    await bot.send_message(chat_id=config.tg_bot.channel,
                           text=f'Имя заказчика: {user_dict[callback.message.chat.id]["name"]}\n'
                                f'Адрес заказчика: {user_dict[callback.message.chat.id]["address"]}\n'
                                f'Номер телефона: {user_dict[callback.message.chat.id]["phone"]}\n'
                                f'Количество угля: {user_dict[callback.message.chat.id]["count"]} кг')


@router.message(Register.address)
async def register_address_error(message: Message):
    logging.info(f'register_address_error: {message.chat.id}')
    await message.answer(text="💬Кажется вы отправили более 4096 символов. Пожалуйста повторите ввод имени")


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
    await callback.message.edit_reply_markup(text='')
    await callback.message.answer(text=f"🙍<b>{callback.from_user.first_name}</b> Добро пожаловать! Я помогу вам, с чего начнем?🏮",
                                  reply_markup=main_menu(),
                                  parse_mode='html')