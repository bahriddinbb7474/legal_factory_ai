from app.db.base import Document
from app.services.current_user import CurrentUser


class DocumentAccessError(PermissionError):
    pass


class DocumentAccessService:
    CATEGORY_ROLES = {
        "hr_document": {"hr", "director", "admin"},
        "client_debt": {"director", "chief_accountant", "accounting", "sales", "admin"},
        "tax_letter": {"director", "chief_accountant", "accounting", "admin"},
        "government_letter": {"director", "chief_accountant", "accounting", "admin"},
        "import_contract": {"director", "chief_accountant", "procurement", "admin"},
        "local_contract": {"director", "sales", "procurement", "chief_accountant", "admin"},
    }
    DEFAULT_ALLOWED_ROLES = {"director", "chief_accountant", "accounting", "sales", "procurement", "hr", "admin"}

    def assert_can_access(self, user: CurrentUser, document: Document, action: str) -> None:
        allowed_roles = self.CATEGORY_ROLES.get(document.category, self.DEFAULT_ALLOWED_ROLES)
        if user.role not in allowed_roles:
            raise DocumentAccessError(f"Role '{user.role}' is not allowed to {action} this document")


document_access_service = DocumentAccessService()
