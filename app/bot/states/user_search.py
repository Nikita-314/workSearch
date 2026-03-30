from aiogram.fsm.state import State, StatesGroup


class UserSearchStates(StatesGroup):
    choosing_city = State()
    typing_city = State()
    choosing_job_type = State()
    choosing_schedule = State()