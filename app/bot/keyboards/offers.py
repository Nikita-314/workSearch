from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def offer_keyboard(offer_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть вакансию",
                    url=offer_url,
                )
            ]
        ]
    )