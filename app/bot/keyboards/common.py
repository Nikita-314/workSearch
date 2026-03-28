from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def subscription_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, присылать",
                    callback_data="subscribe_yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Нет, не нужно",
                    callback_data="subscribe_no",
                )
            ],
        ]
    )
    
def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать подбор")],
        ],
        resize_keyboard=True,
    )