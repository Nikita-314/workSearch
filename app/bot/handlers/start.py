from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.analytics.storage import upsert_user
from app.analytics.events import log_event
from app.bot.keyboards.common import start_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    upsert_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    
    log_event(
        event_name="bot_started",
        user_id=message.from_user.id,
        username=message.from_user.username,
    )

    await message.answer(
        "Привет 👋\n\n"
        "Я помогу подобрать подходящую вакансию.",
        reply_markup=start_keyboard(),
    )

