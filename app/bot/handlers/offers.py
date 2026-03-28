from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.analytics.events import log_event
from app.analytics.storage import save_offer_interaction
from app.bot.services.offers import find_offer_by_id
from app.analytics.storage import set_user_subscription
from app.bot.keyboards.common import subscription_keyboard

router = Router()


@router.callback_query(F.data.startswith("offer_details:"))
async def offer_details_handler(callback: CallbackQuery) -> None:
    offer_id = int(callback.data.split(":")[1])
    offer = find_offer_by_id(offer_id)

    if not offer:
        await callback.answer("Вакансия не найдена", show_alert=True)
        return

    save_offer_interaction(
        telegram_user_id=callback.from_user.id,
        offer_id=offer_id,
        interaction_type="details_opened",
    )

    log_event(
        event_name="offer_details_opened",
        user_id=callback.from_user.id,
        offer_id=offer_id,
        title=offer["title"],
    )

    full_description = (
        offer.get("full_description")
        or "Подробное описание пока не добавлено."
    )

    await callback.message.answer(
        f"<b>{offer['title']} — подробное описание</b>\n\n{full_description}"
    )
    await callback.answer()


@router.callback_query(F.data == "start_new_search")
async def start_new_search_handler(callback: CallbackQuery) -> None:
    log_event(
        event_name="new_search_requested",
        user_id=callback.from_user.id,
    )

    await callback.message.answer(
        "Чтобы начать заново, нажми /search или кнопку «Начать подбор»."
    )
    await callback.answer()

    @router.callback_query(F.data == "subscribe_yes")
async def subscribe_yes_handler(callback: CallbackQuery) -> None:
    set_user_subscription(
        telegram_user_id=callback.from_user.id,
        is_subscribed=True,
    )

    log_event(
        event_name="subscription_enabled",
        user_id=callback.from_user.id,
    )

    await callback.message.answer("Отлично ✅ Теперь я смогу присылать новые подходящие вакансии.")
    await callback.answer()


@router.callback_query(F.data == "subscribe_no")
async def subscribe_no_handler(callback: CallbackQuery) -> None:
    set_user_subscription(
        telegram_user_id=callback.from_user.id,
        is_subscribed=False,
    )

    log_event(
        event_name="subscription_disabled",
        user_id=callback.from_user.id,
    )

    await callback.message.answer("Хорошо, новые вакансии присылать не буду.")
    await callback.answer()