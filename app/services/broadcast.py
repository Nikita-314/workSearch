import asyncio

from aiogram import Bot

from app.analytics.storage import (
    get_matching_subscribed_users,
    was_offer_sent,
    save_outbound_notification,
)
from app.bot.keyboards.offers import offer_keyboard
from app.bot.services.offers import load_offers
from app.bot.services.tracking import build_offer_tracking_link


CHECK_INTERVAL = 60  # каждые 60 секунд


async def broadcast_loop(bot: Bot):
    while True:
        try:
            offers = load_offers()

            for offer in offers:
                users = get_matching_subscribed_users(
                    city=offer["city"],
                    job_type=offer["job_type"],
                    schedule=offer["schedule"],
                )

                for telegram_user_id, username in users:
                    if was_offer_sent(telegram_user_id, offer["id"]):
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