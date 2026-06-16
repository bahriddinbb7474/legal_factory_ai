from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import CostRecord
from app.services.audit import write_audit_log
from app.services.current_user import CurrentUser


class BudgetService:
    async def check_before_call(self, db: AsyncSession, user: CurrentUser) -> None:
        monthly_budget = Decimal(str(settings.monthly_budget_usd))
        if monthly_budget <= 0:
            return

        spent = await self.current_month_spend(db)
        percent = (spent / monthly_budget) * Decimal("100")
        warning_percent = Decimal(settings.budget_warning_percent)
        if percent >= warning_percent:
            await write_audit_log(
                db,
                action="budget.warning",
                entity_type="cost_record",
                entity_id=None,
                user_id=user.id,
                details={"spent": str(spent), "budget": str(monthly_budget), "percent": str(percent)},
            )
        if percent >= 100 and settings.block_expensive_calls and user.role != "admin":
            await write_audit_log(
                db,
                action="budget.block",
                entity_type="cost_record",
                entity_id=None,
                user_id=user.id,
                details={"spent": str(spent), "budget": str(monthly_budget)},
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Месячный бюджет исчерпан. Вызов модели заблокирован настройками.",
            )

    async def current_month_spend(self, db: AsyncSession) -> Decimal:
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        result = await db.execute(select(func.coalesce(func.sum(CostRecord.cost_usd), 0)).where(CostRecord.created_at >= month_start))
        return Decimal(str(result.scalar_one() or 0))


budget_service = BudgetService()
