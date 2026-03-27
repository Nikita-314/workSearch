from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.analytics.events import log_event

router = Router()


@router.callback_query(F.data.startswith("offer_click:"))
async def offer_click_handler(callback: CallbackQuery) -> None:
    offer_id = int(callback.data.split(":")[1])

    log_event(
        event_name="offer_clicked",
        user_id=callback.from_user.id,
        offer_id=offer_id,
    )

    await callback.answer("Переходи по ссылке ниже 👇", show_alert=False)