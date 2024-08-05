from datetime import datetime
from typing import List
import uuid

from app.api.dashboard.model.budget import BudgetCreate, Budget, BudgetUpdate
from sqlmodel import Session, select, delete
from sqlmodel.sql.expression import Select


class BudgetDAO:
    def create(
        self, session: Session, budget_in: BudgetCreate, owner_id: uuid.UUID
    ) -> Budget:
        db_item = Budget.model_validate(budget_in, update={"owner_id": owner_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    def get_budget_list(
        self,
        session: Session,
        owner_id: uuid.UUID,
        start_date: str | None = None,
        end_date: str | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> List[Budget]:
        statement = self.get_budget_list_statement(
            owner_id=owner_id,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by,
            order_type=order_type,
        )
        budgets = session.exec(statement).all()
        return budgets

    def get_budget_list_statement(
        self,
        owner_id: uuid.UUID,
        start_date: str | None = None,
        end_date: str | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> Select:
        statement = select(Budget).where(Budget.owner_id == owner_id)

        if start_date and start_date != "":
            statement = statement.where(Budget.date >= start_date)

        if end_date and end_date != "":
            statement = statement.where(Budget.date <= end_date)

        if order_by and order_by != "":
            # Convert order_by from camel case to snake case
            order_by_snake = "".join(
                ["_" + i.lower() if i.isupper() else i for i in order_by]
            ).lstrip("_")
            order_column = getattr(Budget, order_by_snake)
            statement = statement.order_by(
                order_column.desc() if order_type == "desc" else order_column
            )
        else:
            statement = statement.order_by(Budget.date.desc())

        return statement

    def get_budget_by_id(self, session: Session, id: uuid.UUID) -> Budget:
        budget = session.get(Budget, id)
        return budget

    def get_budget_by_date(
        self, session: Session, owner_id: uuid.UUID, date: str
    ) -> Budget:
        budget = session.exec(
            select(Budget).where(Budget.owner_id == owner_id, Budget.date == date)
        ).first()

        return budget

    def update_budget(
        self, session: Session, current_budget: Budget, budget_in: BudgetUpdate
    ) -> Budget:
        update_dict = budget_in.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(current_budget, key, value)

        session.add(current_budget)
        session.commit()
        session.refresh(current_budget)
        return current_budget

    def delete_budgets(self, session: Session, ids: List[uuid.UUID]) -> bool:
        # Delete budget with items
        budgets = session.exec(select(Budget).where(Budget.id.in_(ids))).all()

        if not budgets or len(budgets) != len(ids):
            return False

        for budget in budgets:
            session.delete(budget)

        session.commit()
        return True


budget_dao = BudgetDAO()
