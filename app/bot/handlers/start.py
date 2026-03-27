from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.analytics.events import log_event

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    log_event(
        event_name="bot_started",
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    
    await message.answer(
        "Привет 👋\n\n"
        "Я помогу подобрать подходящую вакансию.\n"
        "Нажми команду /search, чтобы начать подбор."
    )



