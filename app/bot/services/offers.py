import json
from pathlib import Path


OFFERS_FILE = Path(__file__).resolve().parents[2] / "data" / "offers.json"


def load_offers() -> list[dict]:
    with open(OFFERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_to_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def get_offer_cities(offer: dict) -> list[str]:
    return normalize_to_list(offer.get("city"))


def get_offer_schedules(offer: dict) -> list[str]:
    return normalize_to_list(offer.get("schedule"))


def city_matches(offer_city, selected_city: str) -> bool:
    cities = normalize_to_list(offer_city)
    return "all" in cities or selected_city in cities


def schedule_matches(offer_schedule, selected_schedule: str) -> bool:
    schedules = normalize_to_list(offer_schedule)

    if selected_schedule in schedules:
        return True

    compatible = {
        "Гибкий график": {"Подработка", "Гибкий график"},
        "Подработка": {"Подработка", "Гибкий график"},
    }

    for schedule in schedules:
        if selected_schedule in compatible.get(schedule, set()):
            return True

    return False


def get_city_label(offer: dict) -> str:
    cities = get_offer_cities(offer)
    if not cities:
        return "Не указан"
    if "all" in cities:
        return "Все города"
    return ", ".join(cities)


def get_schedule_label(offer: dict) -> str:
    schedules = get_offer_schedules(offer)
    if not schedules:
        return "Не указан"
    return ", ".join(schedules)


def find_offer_by_id(offer_id: int) -> dict | None:
    offers = load_offers()
    return next((offer for offer in offers if offer["id"] == offer_id), None)


def find_matching_offers(city: str, job_type: str, schedule: str) -> tuple[list[dict], str]:
    offers = load_offers()

    exact_matches = []
    city_job_type_matches = []
    job_type_matches = []

    for offer in offers:
        if (
            city_matches(offer.get("city"), city)
            and job_type in normalize_to_list(offer.get("job_type"))
            and schedule_matches(offer.get("schedule"), schedule)
        ):
            exact_matches.append(offer)

    if exact_matches:
        return exact_matches, "exact"

    for offer in offers:
        if city_matches(offer.get("city"), city) and offer["job_type"] == job_type:
            city_job_type_matches.append(offer)

    if city_job_type_matches:
        return city_job_type_matches, "city_job_type"

    for offer in offers:
        if offer["job_type"] == job_type:
            job_type_matches.append(offer)

    if job_type_matches:
        return job_type_matches, "job_type_only"

    return [], "none"