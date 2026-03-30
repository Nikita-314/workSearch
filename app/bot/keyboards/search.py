from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from app.bot.services.offers import load_offers

POPULAR_CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Казань",
    "Екатеринбург",
]

def city_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Москва"), KeyboardButton(text="Санкт-Петербург")],
            [KeyboardButton(text="Казань"), KeyboardButton(text="Екатеринбург")],
            [KeyboardButton(text="Другой город")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def job_type_keyboard() -> ReplyKeyboardMarkup:
    offers = load_offers()
    job_types = sorted({offer["job_type"] for offer in offers if offer.get("job_type")})

    rows = []
    row = []

    for job_type in job_types:
        row.append(KeyboardButton(text=job_type))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def schedule_keyboard() -> ReplyKeyboardMarkup:
    offers = load_offers()
    schedules = sorted({offer["schedule"] for offer in offers if offer.get("schedule")})

    rows = []
    row = []

    for schedule in schedules:
        row.append(KeyboardButton(text=schedule))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        one_time_keyboard=True,
    )