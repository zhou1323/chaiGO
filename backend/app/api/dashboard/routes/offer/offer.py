from typing import Annotated
from app.api.dashboard.model.offer import (
    Offer,
    OfferPublic,
    ShoppingListContent,
)
from app.api.dashboard.service.offer_service import offer_service
from app.api.deps import CurrentUser, SessionDep
from app.common.response.response_schema import ResponseModel, response_base
from fastapi import APIRouter, Depends, Query
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


@router.post("/send-shopping-list-email")
async def send_shopping_list_email(
    session: SessionDep, current_user: CurrentUser, shopping_list: ShoppingListContent
) -> ResponseModel:
    await offer_service.send_shopping_list_email(
        session=session, current_user=current_user, shopping_list=shopping_list
    )
    return await response_base.success()


@router.get("/recommend-shopping-list")
async def recommend_shopping_list(
    session: SessionDep,
    current_user: CurrentUser,
    weekly_budget: Annotated[str | None, Query(alias="weeklyBudget")] = None,
) -> ResponseModel:
    recommended_shopping_list = offer_service.recommend_shopping_list(
        session=session, current_user=current_user, weekly_budget=weekly_budget
    )
    return await response_base.success(data={"items": recommended_shopping_list})
