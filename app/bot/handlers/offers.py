from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.analytics.events import log_event
from app.analytics.storage import (
    get_matching_subscribed_users,
    save_offer_interaction,
    save_outbound_notification,
    set_user_subscription,
)
from app.bot.keyboards.offers import offer_keyboard
from app.bot.services.offers import find_offer_by_id
from app.bot.services.tracking import build_offer_tracking_link
from app.analytics.storage import was_offer_sent

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

    await callback.message.answer(
        "Отлично ✅ Теперь я смогу присылать новые подходящие вакансии."
    )
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

    await callback.message.answer(
        "Хорошо, новые вакансии присылать не буду."
    )
    await callback.answer()


@router.message(Command("audience"))
async def audience_preview_handler(message: Message) -> None:
    if message.from_user.id != 526213942:
        await message.answer("Эта команда только для администратора.")
        return

    users = get_matching_subscribed_users(
        city="Санкт-Петербург",
        job_type="Курьер",
        schedule="Подработка",
    )

    if not users:
        await message.answer("Подписанных пользователей под этот оффер пока нет.")
        return

    lines = [
        "Найдены подходящие подписанные пользователи:",
        "",
    ]

    for telegram_user_id, username in users[:20]:
        lines.append(f"id={telegram_user_id} | @{username or 'no_username'}")

    lines.append("")
    lines.append(f"Всего: {len(users)}")

    await message.answer("\n".join(lines))


@router.message(Command("send_offer"))
async def send_offer_handler(message: Message) -> None:
    if message.from_user.id != 526213942:
        await message.answer("Нет доступа")
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Используй: /send_offer 6")
        return

    offer_id = int(parts[1])
    offer = find_offer_by_id(offer_id)

    if not offer:
        await message.answer("Оффер не найден")
        return



    users = get_matching_subscribed_users(
        city=offer["city"],
        job_type=offer["job_type"],
        schedule=offer["schedule"],
    )

    if not users:
        await message.answer("Нет подходящих пользователей")
        return

    sent = 0

    for telegram_user_id, username in users:
        if was_offer_sent(telegram_user_id, offer_id):
            continue
        try:
            url = build_offer_tracking_link(
                offer_id=offer["id"],
                user_id=telegram_user_id,
            )

            text = (
                f"<b>{offer['title']}</b>\n"
                f"{offer['salary']}\n\n"
                f"{offer.get('short_description', '')}"
            )

            await message.bot.send_message(
                chat_id=telegram_user_id,
                text="Новая вакансия 👇",
            )

            await message.bot.send_message(
                chat_id=telegram_user_id,
                text=text,
                reply_markup=offer_keyboard(
                    offer_id=offer["id"],
                    offer_url=url,
                ),
            )

            save_outbound_notification(
                telegram_user_id=telegram_user_id,
                offer_id=offer["id"],
                status="sent",
            )
            sent += 1

        except Exception as e:
            print("Ошибка отправки:", e)
            save_outbound_notification(
                telegram_user_id=telegram_user_id,
                offer_id=offer["id"],
                status="failed",
            )

    log_event(
        event_name="offer_broadcast_sent",
        user_id=message.from_user.id,
        offer_id=offer["id"],
        sent_count=sent,
    )

    await message.answer(f"Отправлено: {sent}")