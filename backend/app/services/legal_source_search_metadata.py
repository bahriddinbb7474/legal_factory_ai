import re
import unicodedata
from typing import Protocol


class LegalSourceWithDocumentNumber(Protocol):
    document_number: str | None


# These aliases are curated search metadata for approved first-batch legal sources.
# They help Russian user queries match sources whose imported titles may be English/transliterated.
# Long-term admin-managed aliases can be moved to LegalSource metadata in a later stage.
FIRST_BATCH_SEARCH_ALIASES_BY_DOCUMENT_NUMBER = {
    "zru-547": ("персональные данные",),
    "zru-410": ("охрана труда",),
    "77-ii": ("внешнеэкономическая деятельность",),
    "zru-573": ("валютное регулирование",),
    "zru-819": ("техническое регулирование", "сертификация продукции"),
}


def get_source_search_aliases(source: LegalSourceWithDocumentNumber) -> tuple[str, ...]:
    document_number = _normalize_document_number(source.document_number or "")
    return FIRST_BATCH_SEARCH_ALIASES_BY_DOCUMENT_NUMBER.get(document_number, ())


def _normalize_document_number(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.casefold().strip()
    return re.sub(r"\s+", " ", value)
