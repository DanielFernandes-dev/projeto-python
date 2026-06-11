"""Blueprint de prioridades — CRUD genérico ordenado por level."""
from helpdesk.models.priority import Priority
from helpdesk.resources.base_crud import create_crud_blueprint

priority_bp = create_crud_blueprint(
    "priorities", __name__, Priority,
    list_order_attr=Priority.level,
    create_fields=["name", "level", "color"],
    update_fields=["name", "level", "color", "is_active"],
)
