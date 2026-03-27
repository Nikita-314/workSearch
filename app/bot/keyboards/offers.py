from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def offer_keyboard(offer_id: int, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть вакансию",
                    callback_data=f"offer_click:{offer_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Перейти по ссылке",
                    url=url,
                )
            ],
        ]
    )