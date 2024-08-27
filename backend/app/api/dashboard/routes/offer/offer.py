from app.api.dashboard.model.offer import (
    Offer,
    OfferPublic,
)
from app.api.dashboard.service.offer_service import offer_service
from app.api.deps import SessionDep
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate

router = APIRouter()


@router.get("/list")
async def get_offers_list(
    session: SessionDep,
    description: str | None = None,
    category: str | None = None,
    params: Params = Depends(),
) -> Page[OfferPublic]:
    statement = offer_service.get_offer_list_statement(
        description=description,
        category=category,
    )

    paginated_offers = paginate(session, statement)

    store_dict = {}

    for offer in paginated_offers.items:
        if offer.store_id in store_dict:
            offer.store_name = store_dict[offer.store_id]
        else:
            offer = offer_service.update_offer_store_name(session=session, offer=offer)
            store_dict[offer.store_id] = offer.store_name

        offer = offer_service.update_offer_img_url(offer)
    return paginated_offers
