import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence

from app.schemas.rag import LegalTriggerDetection


@dataclass(frozen=True, slots=True)
class LegalTriggerPattern:
    family: str
    label: str
    expression: str


LEGAL_TRIGGER_PATTERNS = (
    LegalTriggerPattern("tax", "ru:налог*", r"\bналог\w*"),
    LegalTriggerPattern("tax", "uz_lat:soliq*", r"\bsoliq\w*"),
    LegalTriggerPattern("tax", "uz_cyr:солиқ*", r"\bсолиқ\w*"),
    LegalTriggerPattern("fine", "ru:штраф*", r"\bштраф\w*"),
    LegalTriggerPattern("fine", "uz_lat:jarima*", r"\bjarima\w*"),
    LegalTriggerPattern("fine", "uz_cyr:жарима*", r"\bжарима\w*"),
    LegalTriggerPattern("dismissal", "ru:увол*", r"\bувол\w*"),
    LegalTriggerPattern("dismissal", "uz_lat:ishdan_boshat*", r"\bishdan\s+bo'?shat\w*"),
    LegalTriggerPattern("dismissal", "uz_cyr:ишдан_бўшат*", r"\bишдан\s+бўшат\w*"),
    LegalTriggerPattern("contract", "ru:договор*", r"\bдоговор\w*"),
    LegalTriggerPattern("contract", "uz_lat:shartnoma*", r"\bshartnoma\w*"),
    LegalTriggerPattern("contract", "uz_cyr:шартнома*", r"\bшартнома\w*"),
    LegalTriggerPattern("claim", "ru:претензи*", r"\bпретензи\w*"),
    LegalTriggerPattern("claim", "uz_lat:davo*", r"\bda'?vo\w*"),
    LegalTriggerPattern("claim", "uz_cyr:даъво*", r"\bдаъво\w*"),
    LegalTriggerPattern("court", "ru_uz_cyr:суд*", r"\bсуд\w*"),
    LegalTriggerPattern("court", "uz_lat:sud*", r"\bsud\w*"),
    LegalTriggerPattern("government_authority", "ru:госорган*", r"\bгосорган\w*"),
    LegalTriggerPattern(
        "government_authority",
        "ru:государственный_орган*",
        r"\bгосударственн\w*\s+орган\w*",
    ),
    LegalTriggerPattern("government_authority", "uz_lat:davlat_organi*", r"\bdavlat\s+organ\w*"),
    LegalTriggerPattern("government_authority", "uz_cyr:давлат_органи*", r"\bдавлат\s+орган\w*"),
    LegalTriggerPattern("hr_labor", "ru:труд*", r"\bтруд\w*"),
    LegalTriggerPattern("hr_labor", "uz_lat:mehnat*", r"\bmehnat\w*"),
    LegalTriggerPattern("hr_labor", "uz_cyr:меҳнат*", r"\bмеҳнат\w*"),
    LegalTriggerPattern("debt", "ru:долг*", r"\bдолг\w*"),
    LegalTriggerPattern("debt", "ru:задолженн*", r"\bзадолженн\w*"),
    LegalTriggerPattern("debt", "uz_lat:qarz*", r"\bqarz\w*"),
    LegalTriggerPattern("debt", "uz_cyr:қарз*", r"\bқарз\w*"),
    LegalTriggerPattern("customs_import", "ru:импорт*", r"\bимпорт\w*"),
    LegalTriggerPattern("customs_import", "uz_lat:import*", r"\bimport\w*"),
    LegalTriggerPattern("customs_import", "ru:тамож*", r"\bтамож\w*"),
    LegalTriggerPattern("customs_import", "uz_lat:bojxona*", r"\bbojxona\w*"),
    LegalTriggerPattern("customs_import", "uz_cyr:божхона*", r"\bбожхона\w*"),
)


def detect_legal_triggers(
    text: str,
    *,
    patterns: Sequence[LegalTriggerPattern] = LEGAL_TRIGGER_PATTERNS,
) -> LegalTriggerDetection:
    normalized = _normalize_trigger_text(text)
    matched_families: list[str] = []
    matched_patterns: list[str] = []
    for pattern in patterns:
        if not re.search(pattern.expression, normalized):
            continue
        if pattern.family not in matched_families:
            matched_families.append(pattern.family)
        if pattern.label not in matched_patterns:
            matched_patterns.append(pattern.label)
    return LegalTriggerDetection(
        has_legal_trigger=bool(matched_families),
        matched_families=matched_families,
        matched_patterns=matched_patterns,
    )


def _normalize_trigger_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    normalized = normalized.translate(str.maketrans({"‘": "'", "’": "'", "ʻ": "'", "ʼ": "'", "`": "'"}))
    return re.sub(r"\s+", " ", normalized).strip()
