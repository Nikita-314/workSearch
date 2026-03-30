from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.bot.services.offers import load_offers, normalize_to_list


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


def _build_two_column_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    rows = []
    row = []

    for item in items:
        row.append(KeyboardButton(text=item))
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

def job_type_keyboard() -> ReplyKeyboardMarkup:
    offers = load_offers()

    job_types = set()

    for offer in offers:
        value = offer.get("job_type")

        if isinstance(value, list):
            for item in value:
                if item:
                    job_types.add(str(item).strip())
        else:
            if value:
                job_types.add(str(value).strip())

    return _build_two_column_keyboard(sorted(job_types))


def schedule_keyboard() -> ReplyKeyboardMarkup:
    offers = load_offers()

    schedules = set()
    for offer in offers:
        for schedule in normalize_to_list(offer.get("schedule")):
            schedules.add(schedule)

    return _build_two_column_keyboard(sorted(schedules))