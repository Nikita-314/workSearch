from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def city_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Москва"), KeyboardButton(text="Санкт-Петербург")],
            [KeyboardButton(text="Казань"), KeyboardButton(text="Екатеринбург")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def job_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Курьер"), KeyboardButton(text="Склад")],
            [KeyboardButton(text="Удалёнка"), KeyboardButton(text="Колл-центр")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def schedule_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Полный день"), KeyboardButton(text="Подработка")],
            [KeyboardButton(text="Сменный график")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )