from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from app.bot.services.offers import find_matching_offers

from app.bot.keyboards.search import (
    city_keyboard,
    job_type_keyboard,
    schedule_keyboard,
)
from app.bot.states.user_search import UserSearchStates

router = Router()


@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(UserSearchStates.choosing_city)
    await message.answer(
        "Давай подберём вакансию.\n\nВыбери город:",
        reply_markup=city_keyboard(),
    )


@router.message(UserSearchStates.choosing_city)
async def process_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(UserSearchStates.choosing_job_type)
    await message.answer(
        "Хорошо. Теперь выбери тип работы:",
        reply_markup=job_type_keyboard(),
    )


@router.message(UserSearchStates.choosing_job_type)
async def process_job_type(message: Message, state: FSMContext) -> None:
    await state.update_data(job_type=message.text)
    await state.set_state(UserSearchStates.choosing_schedule)
    await message.answer(
        "Какой график тебе нужен?",
        reply_markup=schedule_keyboard(),
    )


@router.message(UserSearchStates.choosing_schedule)
async def process_schedule(message: Message, state: FSMContext) -> None:
    await state.update_data(schedule=message.text)

    data = await state.get_data()

    offers = find_matching_offers(
        city=data["city"],
        job_type=data["job_type"],
        schedule=data["schedule"],
    )

    if not offers:
        await message.answer(
            "По твоему запросу пока нет подходящих вакансий 😔\n\n"
            "Попробуй ещё раз через /search",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    response_lines = [
        "Найденные вакансии ✅",
        "",
    ]

    for offer in offers:
        response_lines.append(
            f"<b>{offer['title']}</b>\n"
            f"Город: {offer['city']}\n"
            f"График: {offer['schedule']}\n"
            f"Зарплата: {offer['salary']}\n"
            f"{offer['description']}\n"
            f"Ссылка: {offer['url']}\n"
        )

    await message.answer(
        "\n".join(response_lines),
        reply_markup=ReplyKeyboardRemove(),
    )

    await state.clear()