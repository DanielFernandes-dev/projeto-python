"""Blueprint de empresas — CRUD genérico com listagem autenticada e GET por ID."""
from helpdesk.models.company import Company
from helpdesk.resources.base_crud import create_crud_blueprint

company_bp = create_crud_blueprint(
    "companies", __name__, Company,
    list_auth=True,
    get_by_id=True,
    create_fields=["name", "cnpj", "email", "phone"],
    update_fields=["name", "cnpj", "email", "phone", "is_active"],
)
