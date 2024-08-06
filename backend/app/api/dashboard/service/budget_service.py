from datetime import datetime
import uuid

from app.api.dashboard.crud.crud_budget import budget_dao
from app.api.dashboard.model.budget import (
    Budget,
    BudgetDetail,
    BudgetCreate,
    BudgetOverview,
    BudgetUpdate,
    BudgetDelete,
)
from app.api.deps import SessionDep, CurrentUser
from fastapi import HTTPException
from sqlmodel.sql.expression import Select


class BudgetService:
    def get_budget_list(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        start_date: str | None = None,
        end_date: str | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> list[Budget]:
        budgets = budget_dao.get_budget_list(
            session=session,
            owner_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by,
            order_type=order_type,
        )
        return budgets

    def get_budget_list_statement(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        start_date: str | None = None,
        end_date: str | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> Select:
        statement = budget_dao.get_budget_list_statement(
            owner_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by,
            order_type=order_type,
        )
        return statement

    def get_current_budget(
        self, session: SessionDep, current_user: CurrentUser
    ) -> Budget:
        current = datetime.now()
        # Change to YYYY-MM format
        current_date = f"{current.year}-{current.month:02d}"

        budget = budget_dao.get_budget_by_date(
            session=session, owner_id=current_user.id, date=current_date
        )

        if not budget:
            return None

        return budget

    def create_budget_from_receipts(
        self, session: SessionDep, current_user: CurrentUser, date: str, amount: float
    ) -> Budget:
        budgets = budget_service.get_budget_list(
            session=session,
            current_user=current_user,
            start_date=date,
            end_date=date,
        )

        if len(budgets) > 0:
            budgets[0].recorded_expense = amount
            session.add(budgets[0])
        else:
            budget_in = BudgetCreate(
                date=date,
                recorded_expense=amount,
            )

            budget_service.create_budget(
                session=session, current_user=current_user, budget_in=budget_in
            )

    def create_budget(
        self, session: SessionDep, current_user: CurrentUser, budget_in: BudgetCreate
    ) -> Budget:
        existed_budget = budget_dao.get_budget_by_date(
            session=session, owner_id=current_user.id, date=budget_in.date
        )

        if existed_budget:
            raise HTTPException(
                status_code=400, detail="Budget for this month already exists"
            )

        budget = budget_dao.create(
            session=session, budget_in=budget_in, owner_id=current_user.id
        )
        return budget

    def update_budget(
        self,
        session: SessionDep,
        id: uuid.UUID,
        current_user: CurrentUser,
        budget_in: BudgetUpdate,
    ) -> Budget:
        budget = budget_dao.get_budget_by_id(session=session, id=id)
        if not budget:
            raise HTTPException(status_code=404, detail="Item not found")
        update_budget = budget_dao.update_budget(
            session=session, current_budget=budget, budget_in=budget_in
        )
        return update_budget

    def delete_budgets(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        budgets_to_delete: BudgetDelete,
    ) -> None:
        result = budget_dao.delete_budgets(session=session, ids=budgets_to_delete.ids)
        if not result:
            raise HTTPException(status_code=404, detail="Budgets not found")

    def get_budgets_overview(
        self, session: SessionDep, current_user: CurrentUser
    ) -> list[BudgetOverview]:
        current = datetime.now()
        start_date = f"{current.year-1}-01"
        end_date = f"{current.year}-12"
        budgets = budget_dao.get_budget_list(
            session=session,
            owner_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

        # Group budgets by month
        budget_dict = {}
        for budget in budgets:
            date = datetime.strptime(budget.date, "%Y-%m")
            overview_data = {"month": date.month}
            if date.year == current.year:
                overview_data["current_year"] = budget
            else:
                overview_data["last_year"] = budget

            if date.month not in budget_dict:
                budget_dict[date.month] = overview_data
            else:
                budget_dict[date.month].update(overview_data)

        return list(budget_dict.values())


budget_service = BudgetService()
