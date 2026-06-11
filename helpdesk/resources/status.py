from helpdesk.models.status import Status
from helpdesk.resources.base_crud import create_crud_blueprint

status_bp = create_crud_blueprint(
    "statuses", __name__, Status,
    list_order_attr=Status.order,
    create_fields=["name", "description", "color", "is_final", "order"],
    update_fields=["name", "description", "color", "is_final", "order", "is_active"],
)
