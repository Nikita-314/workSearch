import asyncio

from aiogram import Bot

from app.analytics.storage import (
    get_matching_subscribed_users,
    save_outbound_notification,
    was_offer_sent,
)
from app.bot.keyboards.offers import offer_keyboard
from app.bot.services.offers import (
    get_offer_cities,
    get_offer_schedules,
    get_schedule_label,
    load_offers,
)
from app.bot.services.tracking import build_offer_tracking_link


CHECK_INTERVAL = 60  # каждые 60 секунд


def pick_broadcast_city(offer: dict) -> str:
    cities = get_offer_cities(offer)
    if not cities or "all" in cities:
        return "all"
    return cities[0]


def pick_broadcast_schedule(offer: dict) -> str:
    schedules = get_offer_schedules(offer)
    if not schedules:
        return "Не указан"
    if "Гибкий график" in schedules:
        return "Гибкий график"
    if "Подработка" in schedules:
        return "Подработка"
    return schedules[0]


async def broadcast_loop(bot: Bot):
    while True:
        try:
            offers = load_offers()

            for offer in offers:
                users = get_matching_subscribed_users(
                    city=pick_broadcast_city(offer),
                    job_type=offer["job_type"],
                    schedule=pick_broadcast_schedule(offer),
                )

                for row in users:
                    telegram_user_id, username = row[:2]

                    if was_offer_sent(telegram_user_id, offer["id"]):
                        continue

                    try:
                        url = build_offer_tracking_link(
                            offer_id=offer["id"],
                            user_id=telegram_user_id,
                        )

                        text = (
                            f"<b>{offer['title']}</b>\n"
                            f"{offer['salary']}\n"
                            f"График: {get_schedule_label(offer)}\n\n"
                            f"{offer.get('short_description', offer.get('description', ''))}"
                        )

                        await bot.send_message(
                            chat_id=telegram_user_id,
                            text="Новая вакансия 👇",
                        )

                        await bot.send_message(
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

                    except Exception:
                        save_outbound_notification(
                            telegram_user_id=telegram_user_id,
                            offer_id=offer["id"],
                            status="failed",
                        )

        except Exception as e:
            print("Broadcast error:", e)

        await asyncio.sleep(CHECK_INTERVAL)