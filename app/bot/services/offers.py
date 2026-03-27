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
    {
        "id": 5,
        "title": "Курьер в Санкт-Петербурге",
        "city": "Санкт-Петербург",
        "job_type": "Курьер",
        "schedule": "Полный день",
        "salary": "от 85 000 ₽",
        "description": "Доставка заказов по городу, можно без опыта.",
        "url": "https://example.com/offer/5",
    },
]


def find_matching_offers(city: str, job_type: str, schedule: str) -> tuple[list[dict], str]:
    exact_matches = []
    city_job_type_matches = []
    job_type_matches = []

    for offer in OFFERS:
        if (
            offer["city"] == city
            and offer["job_type"] == job_type
            and offer["schedule"] == schedule
        ):
            exact_matches.append(offer)

    if exact_matches:
        return exact_matches, "exact"

    for offer in OFFERS:
        if offer["city"] == city and offer["job_type"] == job_type:
            city_job_type_matches.append(offer)

    if city_job_type_matches:
        return city_job_type_matches, "city_job_type"

    for offer in OFFERS:
        if offer["job_type"] == job_type:
            job_type_matches.append(offer)

    if job_type_matches:
        return job_type_matches, "job_type_only"

    return [], "none"