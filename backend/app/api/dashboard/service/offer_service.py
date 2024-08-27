from datetime import datetime
import uuid

from app.api.dashboard.crud.crud_offer import offer_dao
from app.api.dashboard.model.offer import (
    Offer,
    OfferPublic,
)
from app.core.cloudfront import cloudfront_client
from app.api.deps import SessionDep
from app.api.dashboard.service.store_service import store_service
from sqlmodel.sql.expression import Select


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


offer_service = OfferService()
