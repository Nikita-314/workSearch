import json
from pathlib import Path


OFFERS_FILE = Path(__file__).resolve().parents[2] / "data" / "offers.json"


def load_offers() -> list[dict]:
    with open(OFFERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def city_matches(offer_city: str, selected_city: str) -> bool:
    return offer_city == selected_city or offer_city == "all"


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
            city_matches(offer["city"], city)
            and offer["job_type"] == job_type
            and offer["schedule"] == schedule
        ):
            exact_matches.append(offer)

    if exact_matches:
        return exact_matches, "exact"

    for offer in offers:
        if city_matches(offer["city"], city) and offer["job_type"] == job_type:
            city_job_type_matches.append(offer)

    if city_job_type_matches:
        return city_job_type_matches, "city_job_type"

    for offer in offers:
        if offer["job_type"] == job_type:
            job_type_matches.append(offer)

    if job_type_matches:
        return job_type_matches, "job_type_only"

    return [], "none"