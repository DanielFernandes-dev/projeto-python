"""Blueprint de categorias — CRUD genérico via create_crud_blueprint."""
from helpdesk.models.category import Category
from helpdesk.resources.base_crud import create_crud_blueprint

category_bp = create_crud_blueprint(
    "categories", __name__, Category,
    create_fields=["name", "description"],
    update_fields=["name", "description", "is_active"],
)
