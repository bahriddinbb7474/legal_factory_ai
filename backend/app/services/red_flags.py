import re
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Chat, RedFlagRule
from app.services.audit import write_audit_log


RED_FLAG_SEEDS = [
    ("employee_dismissal", "Увольнение сотрудника", ["увольнение", "расторжение трудового", "дисциплинар"], "hr", None, "director"),
    ("tax_authority_response", "Ответ налоговому органу", ["гни", "налог", "камеральная", "ндс"], "tax", None, "chief_accountant"),
    ("government_authority_response", "Ответ госоргану", ["госорган", "предписание", "запрос государственного", "инспекция"], "government", None, "director"),
    ("debt_admission", "Признание долга", ["признать долг", "признание долга", "гарантийное письмо", "задолженность"], "debt", None, "chief_accountant"),
    ("import_contract_signing", "Подписание импортного контракта", ["импортный контракт", "incoterms", "китай", "тамож"], "import", None, "director"),
    ("import_contract_change", "Изменение импортного контракта", ["допсоглашение к импорт", "изменить импортный", "валютный контракт"], "import", None, "director"),
    ("court_claim", "Судебный спор", ["иск", "суд", "арбитраж", "претензия в суд"], "court", None, "director"),
    ("fine_or_penalty", "Штраф или пеня", ["штраф", "пеня", "санкция", "неустойка"], "finance", None, "chief_accountant"),
    ("personal_data", "Персональные данные", ["персональные данные", "паспорт", "пинфл"], "privacy", None, "director"),
    ("workplace_accident", "Несчастный случай", ["несчастный случай", "травма", "охрана труда"], "safety", None, "director"),
    ("amount_above_threshold", "Сумма выше порога", [], "finance", Decimal("100000"), "director"),
]


@dataclass
class RedFlagMatch:
    code: str
    title: str
    required_approver: str


class RedFlagService:
    async def ensure_seed_rules(self, db: AsyncSession) -> None:
        for code, title, keywords, category, threshold, approver in RED_FLAG_SEEDS:
            result = await db.execute(select(RedFlagRule).where(RedFlagRule.code == code))
            if result.scalar_one_or_none() is None:
                db.add(
                    RedFlagRule(
                        code=code,
                        title=title,
                        keywords=keywords,
                        category=category,
                        amount_threshold=threshold,
                        is_enabled=True,
                        required_approver=approver,
                    )
                )
        await db.flush()

    async def detect(self, db: AsyncSession, text: str) -> list[RedFlagMatch]:
        await self.ensure_seed_rules(db)
        result = await db.execute(select(RedFlagRule).where(RedFlagRule.is_enabled.is_(True)))
        rules = list(result.scalars().all())
        normalized = text.casefold()
        matches: list[RedFlagMatch] = []
        for rule in rules:
            keyword_hit = any(keyword.casefold() in normalized for keyword in (rule.keywords or []))
            amount_hit = False
            if rule.amount_threshold is not None:
                amount_hit = _max_amount(normalized) >= Decimal(rule.amount_threshold)
            if keyword_hit or amount_hit:
                matches.append(RedFlagMatch(rule.code, rule.title, rule.required_approver))
        return matches

    async def apply_to_chat(
        self,
        db: AsyncSession,
        chat: Chat,
        text: str,
        user_id: int | None = None,
    ) -> list[RedFlagMatch]:
        matches = await self.detect(db, text)
        if matches:
            previous_status = chat.approval_status
            chat.approval_status = "needs_review"
            chat.status = "needs_review"
            await write_audit_log(
                db,
                action="red_flag.detected",
                entity_type="chat",
                entity_id=chat.id,
                user_id=user_id,
                details={
                    "codes": [match.code for match in matches],
                    "previous_status": previous_status,
                    "new_status": chat.approval_status,
                },
            )
        return matches


def _max_amount(text: str) -> Decimal:
    amounts = []
    for match in re.findall(r"\b\d[\d\s]{4,}(?:[.,]\d+)?\b", text):
        cleaned = match.replace(" ", "").replace(",", ".")
        try:
            amounts.append(Decimal(cleaned))
        except Exception:
            continue
    return max(amounts, default=Decimal("0"))


red_flag_service = RedFlagService()
