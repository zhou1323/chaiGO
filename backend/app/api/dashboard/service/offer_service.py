from datetime import datetime
import json
import uuid

from app.api.dashboard.crud.crud_offer import offer_dao
from app.api.dashboard.model.offer import (
    Offer,
    OfferPublic,
    ShoppingListContent,
)
from app.core.cloudfront import cloudfront_client
from app.api.deps import CurrentUser, SessionDep
from app.api.dashboard.service.store_service import store_service
from app.utils.utils import generate_shopping_list_email, send_email
from fastapi import HTTPException
from sqlmodel.sql.expression import Select
from app.core.openai import openai_client


class OfferService:
    def get_offer_list(
        self,
        session: SessionDep,
        description: str | None = None,
        category: str | None = None,
    ) -> list[Offer]:
        offers = offer_dao.get_offer_list(
            session=session,
            description=description,
            category=category,
        )
        return offers

    def get_offer_list_statement(
        self,
        description: str | None = None,
        category: str | None = None,
    ) -> Select:
        statement = offer_dao.get_offer_list_statement(
            description=description,
            category=category,
        )
        return statement

    def update_offer_store_name(self, session: SessionDep, offer: OfferPublic):
        if offer.store_id:
            store = store_service.get_store_by_id(session=session, id=offer.store_id)
            offer.store_name = store.name
        return offer

    def update_offer_img_url(self, offer: OfferPublic):
        if offer.img:
            offer.img_url = cloudfront_client.generate_url(offer.img)
        return offer

    async def send_shopping_list_email(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        shopping_list: ShoppingListContent,
    ):
        email_data = generate_shopping_list_email(
            email_to=current_user.email,
            shopping_list_content=shopping_list,
        )
        await send_email(
            email_to=current_user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    def recommend_shopping_list(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        weekly_budget: str,
    ):
        shopping_list = []
        offers = self.get_offer_list(session=session)
        offer_info = []
        for offer in offers:
            offer_info.append(
                {
                    "id": str(offer.id),
                    "name": offer.item_en,
                    "price": offer.price,
                    "unit_range_from": offer.unit_range_from,
                    "unit_range_to": offer.unit_range_to,
                    "unit": offer.unit,
                    "ordinary_price": offer.ordinary_price,
                    "store_name": offer.store.name,
                }
            )
        offers_string = json.dumps(offer_info)
        response = openai_client.gpt_4o_generate_shopping_list_with_completion(
            budget_string=weekly_budget, offers_string=offers_string
        )
        if not response:
            raise HTTPException(
                status_code=400,
                detail="Unable to generate shopping list recommendation",
            )

        for offer in response["offers"]:
            id, quantity = offer["id"], offer["quantity"]
            selected_offers = [offer for offer in offers if str(offer.id) == id]
            if len(selected_offers) > 0:
                selected_offer = selected_offers[0]
                img_url = cloudfront_client.generate_url(selected_offer.img)

                for _ in range(quantity):
                    new_id = uuid.uuid4()
                    shopping_list.append(
                        OfferPublic(
                            **selected_offer.model_dump(exclude={"id"}),
                            id=new_id,
                            store_name=selected_offer.store.name,
                            img_url=img_url,
                        )
                    )

        return shopping_list


offer_service = OfferService()
