from pathlib import Path
from app.bot.services.offers import get_offer_schedules
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto, Message, ReplyKeyboardRemove

from app.analytics.events import log_event
from app.analytics.storage import save_offer_interaction, save_user_preferences
from app.bot.keyboards.common import subscription_keyboard
from app.bot.keyboards.offers import offer_keyboard
from app.bot.keyboards.search import city_keyboard, job_type_keyboard, schedule_keyboard
from app.bot.services.offers import find_matching_offers
from app.bot.services.tracking import build_offer_tracking_link
from app.bot.states.user_search import UserSearchStates
from app.bot.services.offers import (
    find_matching_offers,
    get_city_label,
    get_schedule_label,
)

router = Router()


@router.message(F.text == "Начать подбор")
async def start_search_button(message: Message, state: FSMContext) -> None:
    log_event(
        event_name="quiz_started",
        user_id=message.from_user.id,
        username=message.from_user.username,
        source="button",
    )

    await state.set_state(UserSearchStates.choosing_city)
    await message.answer(
        "Давай подберём вакансию.\n\nВыбери город или нажми «Другой город»:",
        reply_markup=city_keyboard(),
    )


@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext) -> None:
    log_event(
        event_name="quiz_started",
        user_id=message.from_user.id,
        username=message.from_user.username,
        source="command",
    )

    await state.set_state(UserSearchStates.choosing_city)
    await message.answer(
        "Давай подберём вакансию.\n\nВыбери город или нажми «Другой город»:",
        reply_markup=city_keyboard(),
    )


@router.message(UserSearchStates.choosing_city, F.text == "Другой город")
async def ask_manual_city(message: Message, state: FSMContext) -> None:
    await state.set_state(UserSearchStates.typing_city)
    await message.answer(
        "Напиши свой город сообщением.\n\n"
        "Даже если его нет в кнопках, я всё равно попробую подобрать подходящие вакансии.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(UserSearchStates.typing_city)
async def process_manual_city(message: Message, state: FSMContext) -> None:
    city = message.text.strip()

    await state.update_data(city=city)

    log_event(
        event_name="city_selected",
        user_id=message.from_user.id,
        city=city,
        source="manual_input",
    )

    await state.set_state(UserSearchStates.choosing_job_type)
    await message.answer(
        "Хорошо. Теперь выбери тип работы:",
        reply_markup=job_type_keyboard(),
    )


@router.message(UserSearchStates.choosing_city)
async def process_city(message: Message, state: FSMContext) -> None:
    city = message.text.strip()

    await state.update_data(city=city)

    log_event(
        event_name="city_selected",
        user_id=message.from_user.id,
        city=city,
        source="keyboard",
    )

    await state.set_state(UserSearchStates.choosing_job_type)
    await message.answer(
        "Хорошо. Теперь выбери тип работы:",
        reply_markup=job_type_keyboard(),
    )


@router.message(UserSearchStates.choosing_job_type)
async def process_job_type(message: Message, state: FSMContext) -> None:
    await state.update_data(job_type=message.text)

    log_event(
        event_name="job_type_selected",
        user_id=message.from_user.id,
        job_type=message.text,
    )

    await state.set_state(UserSearchStates.choosing_schedule)
    await message.answer(
        "Какой график тебе нужен?",
        reply_markup=schedule_keyboard(),
    )


async def send_offer_photos(message: Message, offer: dict) -> None:
    images = offer.get("images", [])

    if not images:
        return

    resolved_paths = [Path(image_path) for image_path in images if Path(image_path).exists()]

    if not resolved_paths:
        return

    if len(resolved_paths) == 1:
        await message.answer_photo(photo=FSInputFile(resolved_paths[0]))
        return

    media_group = [InputMediaPhoto(media=FSInputFile(path)) for path in resolved_paths]
    await message.answer_media_group(media_group)


@router.message(UserSearchStates.choosing_schedule)
async def process_schedule(message: Message, state: FSMContext) -> None:
    await state.update_data(schedule=message.text)

    log_event(
        event_name="schedule_selected",
        user_id=message.from_user.id,
        schedule=message.text,
    )

    data = await state.get_data()

    save_user_preferences(
        telegram_user_id=message.from_user.id,
        city=data["city"],
        job_type=data["job_type"],
        schedule=data["schedule"],
    )

    offers, match_type = find_matching_offers(
        city=data["city"],
        job_type=data["job_type"],
        schedule=data["schedule"],
    )

    log_event(
        event_name="quiz_completed",
        user_id=message.from_user.id,
        city=data["city"],
        job_type=data["job_type"],
        schedule=data["schedule"],
        offers_found=len(offers),
        match_type=match_type,
    )

    if not offers:
        log_event(
            event_name="no_offers_found",
            user_id=message.from_user.id,
            city=data["city"],
            job_type=data["job_type"],
            schedule=data["schedule"],
        )

        await message.answer(
            "По твоему запросу пока нет точных совпадений.\n\n"
            "Но это не значит, что вакансий в твоём городе нет. "
            "Мы постепенно расширяем базу и можем присылать новые варианты позже.",
            reply_markup=ReplyKeyboardRemove(),
        )

        await message.answer(
            "Хочешь, я буду присылать новые подходящие вакансии?",
            reply_markup=subscription_keyboard(),
        )

        await state.clear()
        return

    if match_type == "exact":
        intro_text = "Найдены точные совпадения ✅"
    elif match_type == "city_job_type":
        intro_text = (
            "Точных совпадений по графику не нашлось.\n"
            "Но я нашёл похожие вакансии в твоём городе ✅"
        )
    else:
        intro_text = (
            "Точных совпадений в твоём городе не нашлось.\n"
            "Показываю подходящие вакансии по выбранному направлению ✅"
        )

    await message.answer(
        intro_text,
        reply_markup=ReplyKeyboardRemove(),
    )

    for offer in offers:
        log_event(
            event_name="offer_shown",
            user_id=message.from_user.id,
            offer_id=offer["id"],
            title=offer["title"],
            match_type=match_type,
        )

        save_offer_interaction(
            telegram_user_id=message.from_user.id,
            offer_id=offer["id"],
            interaction_type="shown",
        )

        await send_offer_photos(message, offer)

        tracked_url = build_offer_tracking_link(
            offer_id=offer["id"],
            user_id=message.from_user.id,
        )

        city_label = "Все города" if offer["city"] == "all" else offer["city"]

        offer_text = (
            f"<b>{offer['title']}</b>\n"
            f"Город: {get_city_label(offer)}\n"
            f"График: {get_schedule_label(offer)}\n"
            f"Зарплата: {offer['salary']}\n\n"
            f"{offer.get('short_description') or offer.get('description', 'Описание пока не добавлено.')}"
        )

        await message.answer(
            offer_text,
            reply_markup=offer_keyboard(
                offer_id=offer["id"],
                offer_url=tracked_url,
            ),
        )

    await message.answer(
        "Хочешь, я буду присылать новые подходящие вакансии?",
        reply_markup=subscription_keyboard(),
    )

    await state.clear()