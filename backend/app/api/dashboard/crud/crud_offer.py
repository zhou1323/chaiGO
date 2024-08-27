from typing import List

from app.api.dashboard.model.offer import Offer
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select


class OfferDAO:
    def get_offer_list(
        self,
        session: Session,
        description: str | None = None,
        category: str | None = None,
    ) -> List[Offer]:
        statement = self.get_offer_list_statement(
            description=description,
            category=category,
        )
        offers = session.exec(statement).all()
        return offers

    def get_offer_list_statement(
        self,
        description: str | None = None,
        category: str | None = None,
    ) -> Select:
        statement = select(Offer)

        if description and description != "":
            statement = statement.where(Offer.description == description)

        if category and category != "":
            statement = statement.where(Offer.category == category)

        return statement


offer_dao = OfferDAO()
