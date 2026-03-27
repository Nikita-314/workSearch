from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.analytics.events import log_event
from app.bot.services.offers import load_offers

router = APIRouter()


@router.get("/r/{offer_id}")
async def redirect_to_offer(offer_id: int, user_id: int | None = None):
    offers = load_offers()
    offer = next((item for item in offers if item["id"] == offer_id), None)

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    log_event(
        event_name="offer_redirected",
        user_id=user_id or 0,
        offer_id=offer_id,
        title=offer["title"],
        target_url=offer["url"],
    )

    return RedirectResponse(url=offer["url"], status_code=302)