from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.repositories.user_repository import UserRepository

dashboard_bp = Blueprint("dashboard", __name__)
ticket_repo = TicketRepository()
user_repo = UserRepository()


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def dashboard():
    stats = ticket_repo.dashboard_stats()
    return jsonify({
        "tickets": stats,
        "users": {
            "total": len(user_repo.find_all(is_active=True)),
            "technicians": user_repo.count_by_role("technician"),
            "clients": user_repo.count_by_role("client"),
        },
    }), 200
