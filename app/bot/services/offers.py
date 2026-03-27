OFFERS = [
    {
        "id": 1,
        "title": "Курьер",
        "city": "Москва",
        "job_type": "Курьер",
        "schedule": "Подработка",
        "salary": "от 90 000 ₽",
        "description": "Гибкий график, можно без опыта.",
        "url": "https://example.com/offer/1",
    },
    {
        "id": 2,
        "title": "Сотрудник склада",
        "city": "Санкт-Петербург",
        "job_type": "Склад",
        "schedule": "Полный день",
        "salary": "от 75 000 ₽",
        "description": "Работа на складе, оформление по ТК.",
        "url": "https://example.com/offer/2",
    },
    {
        "id": 3,
        "title": "Оператор колл-центра",
        "city": "Казань",
        "job_type": "Колл-центр",
        "schedule": "Сменный график",
        "salary": "от 60 000 ₽",
        "description": "Можно без опыта, обучение с нуля.",
        "url": "https://example.com/offer/3",
    },
    {
        "id": 4,
        "title": "Удалённый менеджер",
        "city": "Екатеринбург",
        "job_type": "Удалёнка",
        "schedule": "Полный день",
        "salary": "от 70 000 ₽",
        "description": "Удалённая работа из дома.",
        "url": "https://example.com/offer/4",
    },
]


def find_matching_offers(city: str, job_type: str, schedule: str) -> list[dict]:
    matched_offers = []

    for offer in OFFERS:
        if (
            offer["city"] == city
            and offer["job_type"] == job_type
            and offer["schedule"] == schedule
        ):
            matched_offers.append(offer)

    return matched_offers
    


    