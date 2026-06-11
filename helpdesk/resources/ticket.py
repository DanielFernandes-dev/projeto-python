from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpdesk.services.ticket_service import TicketService
from helpdesk.utils.decorators import role_required
from helpdesk.utils.helpers import parse_pagination

ticket_bp = Blueprint("tickets", __name__)
service = TicketService()


@ticket_bp.route("", methods=["GET"])
@jwt_required()
def list_tickets():
    page, per_page = parse_pagination()
    return jsonify(service.list_tickets(
        page=page, per_page=per_page,
        status_id=request.args.get("status_id", type=int),
        priority_id=request.args.get("priority_id", type=int),
        category_id=request.args.get("category_id", type=int),
        created_by_id=request.args.get("created_by_id", type=int),
        assigned_to_id=request.args.get("assigned_to_id", type=int),
    )), 200


@ticket_bp.route("/<int:ticket_id>", methods=["GET"])
@jwt_required()
def get_ticket(ticket_id):
    ticket = service.get_by_id(ticket_id)
    return jsonify(ticket.to_dict()), 200


@ticket_bp.route("/protocol/<string:protocol>", methods=["GET"])
@jwt_required()
def get_ticket_by_protocol(protocol):
    ticket = service.get_by_protocol(protocol)
    return jsonify(ticket.to_dict()), 200


@ticket_bp.route("", methods=["POST"])
@jwt_required()
def create_ticket():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    if not data.get("title") or not data.get("description"):
        return jsonify({"error": "Título e descrição são obrigatórios"}), 422
    ticket = service.create(data, user_id)
    return jsonify(ticket.to_dict()), 201


@ticket_bp.route("/<int:ticket_id>", methods=["PUT"])
@jwt_required()
def update_ticket(ticket_id):
    data = request.get_json() or {}
    ticket = service.update(ticket_id, data)
    return jsonify(ticket.to_dict()), 200


@ticket_bp.route("/<int:ticket_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_ticket(ticket_id):
    service.delete(ticket_id)
    return jsonify({"message": "Ticket removido"}), 200


@ticket_bp.route("/<int:ticket_id>/assign", methods=["POST"])
@jwt_required()
@role_required("admin", "technician")
def assign_ticket(ticket_id):
    data = request.get_json() or {}
    technician_id = data.get("technician_id")
    if not technician_id:
        return jsonify({"error": "technician_id é obrigatório"}), 422
    ticket = service.assign(ticket_id, technician_id)
    return jsonify(ticket.to_dict()), 200


@ticket_bp.route("/<int:ticket_id>/comments", methods=["GET"])
@jwt_required()
def list_comments(ticket_id):
    ticket = service.get_by_id(ticket_id)
    current_user_id = int(get_jwt_identity())
    from helpdesk.models.user import User
    user = User.query.get(current_user_id)
    comments = ticket.comments.all()
    if user and user.role == "client":
        comments = [c for c in comments if not c.is_internal]
    return jsonify({
        "comments": [c.to_dict() for c in comments],
        "total": len(comments),
    }), 200


@ticket_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(ticket_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    if not data.get("content"):
        return jsonify({"error": "Conteúdo do comentário é obrigatório"}), 422
    comment = service.add_comment(ticket_id, data, user_id)
    return jsonify(comment.to_dict()), 201
