from app.core.config import settings


def build_offer_tracking_link(offer_id: int, user_id: int) -> str:
    return f"{settings.base_url}/r/{offer_id}?user_id={user_id}"