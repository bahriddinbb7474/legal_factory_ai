from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import LegalSource
from app.schemas.legal_sources import LegalSourceInventoryItem


MAX_LEGAL_SOURCE_INVENTORY_LIMIT = 200


async def build_legal_source_inventory(
    db: AsyncSession,
    *,
    limit: int | None = None,
    as_of: datetime | None = None,
) -> list[LegalSourceInventoryItem]:
    """Return deterministic metadata for sources eligible for ordinary legal RAG."""
    effective_limit = settings.legal_source_inventory_limit if limit is None else limit
    if effective_limit < 1:
        raise ValueError("legal source inventory limit must be positive")
    effective_limit = min(effective_limit, MAX_LEGAL_SOURCE_INVENTORY_LIMIT)

    inventory_time = as_of or datetime.utcnow()
    result = await db.execute(
        select(LegalSource)
        .where(
            LegalSource.status == "active",
            LegalSource.official_status == "official",
        )
        .order_by(LegalSource.id.asc())
        .limit(effective_limit)
    )
    return [_to_inventory_item(source, inventory_time) for source in result.scalars().all()]


def _to_inventory_item(source: LegalSource, as_of: datetime) -> LegalSourceInventoryItem:
    return LegalSourceInventoryItem(
        legal_source_id=source.id,
        title=source.title,
        document_type=source.document_type,
        document_number=source.document_number,
        adoption_date=source.adoption_date,
        revision_date=source.revision_date,
        language=source.language,
        status=source.status,
        official_status=source.official_status,
        source_url=source.source_url,
        last_checked_at=source.last_checked_at,
        next_check_due_at=source.next_check_due_at,
        freshness_warning=source.next_check_due_at is not None and source.next_check_due_at < as_of,
    )
