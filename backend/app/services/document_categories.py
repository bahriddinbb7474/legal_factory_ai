from pathlib import Path


DOCUMENT_CATEGORIES = {
    "local_contract",
    "import_contract",
    "client_debt",
    "tax_letter",
    "government_letter",
    "hr_document",
    "order",
    "occupational_safety",
    "certificate",
    "template",
    "other",
}


def suggest_category(filename: str, extracted_text: str) -> str:
    haystack = f"{Path(filename).name} {extracted_text}".lower()
    rules = [
        ("import_contract", ["import", "инвойс", "invoice", "china", "китай", "customs", "тамож"]),
        ("client_debt", ["debt", "задолж", "претенз", "оплат", "сверк"]),
        ("tax_letter", ["налог", "ндс", "гни", "tax"]),
        ("government_letter", ["гос", "министер", "hokim", "adliya", "орган"]),
        ("hr_document", ["hr", "кадр", "труд", "приказ", "сотрудник", "дисциплин"]),
        ("occupational_safety", ["охрана труда", "safety", "техника безопасности"]),
        ("certificate", ["сертификат", "certificate"]),
        ("template", ["template", "шаблон"]),
        ("local_contract", ["договор", "contract", "поставка", "аренда"]),
        ("order", ["order", "заказ", "поручение"]),
    ]
    for category, keywords in rules:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "other"
