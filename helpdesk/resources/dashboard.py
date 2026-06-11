"""Blueprint do dashboard — estatísticas agregadas de tickets e usuários.

Endpoint único que retorna totais, contagem de abertos/fechados,
últimos 5 tickets criados e quantidade de usuários por papel.
Acesso requer autenticação JWT.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.models.ticket import Ticket
from helpdesk.models.status import Status
from helpdesk.models.user import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def dashboard():
    total = Ticket.query.count()
    closed_ids = [s.id for s in Status.query.filter_by(is_final=True).all()]
    open_count = Ticket.query.filter(~Ticket.status_id.in_(closed_ids)).count() if closed_ids else total
    closed_count = Ticket.query.filter(Ticket.status_id.in_(closed_ids)).count() if closed_ids else 0
    recent = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()

    return jsonify({
        "tickets": {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "recent": [t.to_dict() for t in recent],
        },
        "users": {
            "total": User.query.filter_by(is_active=True).count(),
            "technicians": User.query.filter_by(role="technician").count(),
            "clients": User.query.filter_by(role="client").count(),
        },
    }), 200
