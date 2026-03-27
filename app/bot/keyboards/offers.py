from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def offer_keyboard(offer_id: int, offer_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть вакансию",
                    url=offer_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Подробнее",
                    callback_data=f"offer_details:{offer_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Новый подбор",
                    callback_data="start_new_search",
                )
            ],
        ]
    )