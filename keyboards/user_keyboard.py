import logging
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu():
    logging.info("keyboards_main_menu")
    button_1 = KeyboardButton(text='Заказать уголь 💷')
    button_2 = KeyboardButton(text='Наш канал 🧧')
    button_3 = KeyboardButton(text='Техподдержка ☎️')
    button_4 = KeyboardButton(text='О нас❓')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_2], [button_3, button_4]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="🎯Выберите действие"
    )
    return keyboard


def keyboards_manager_link():
    button_1 = InlineKeyboardButton(text="Менеджер🦾", url="t.me/Sweeteeboy")
    button_2 = InlineKeyboardButton(text='Назад', callback_data='main_menu')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]], )
    return keyboard


def keyboards_get_phone():
    button_1 = KeyboardButton(text='Поделиться контактом ☎️', request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def keyboards_chanel_link():
    button_1 = InlineKeyboardButton(text='Подписаться', url='t.me/thecococoal')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], ], )
    return keyboard


def keyboards_back_main_menu(text: str = 'Назад'):
    button_1 = InlineKeyboardButton(text=text, callback_data='main_menu')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], ], )
    return keyboard


def keyboards_confirm_register():
    button_1 = InlineKeyboardButton(text='Подтвердить', callback_data='confirm_register')
    button_2 = InlineKeyboardButton(text='Назад', callback_data='main_menu')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], ], )
    return keyboard
