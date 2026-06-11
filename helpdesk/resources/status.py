from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.models.status import Status
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.decorators import role_required
from helpdesk.utils.extensions import db

status_bp = Blueprint("statuses", __name__)
repo = BaseRepository(Status)


@status_bp.route("", methods=["GET"])
def list_statuses():
    statuses = Status.query.filter_by(is_active=True).order_by(Status.order).all()
    return jsonify({"statuses": [s.to_dict() for s in statuses]}), 200


@status_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_status():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 422
    status = Status(
        name=data["name"],
        description=data.get("description"),
        color=data.get("color", "#808080"),
        is_final=data.get("is_final", False),
        order=data.get("order", 0),
    )
    return jsonify(repo.save(status).to_dict()), 201


@status_bp.route("/<int:status_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_status(status_id):
    status = repo.find_by_id(status_id)
    if not status:
        return jsonify({"error": "Status não encontrado"}), 404
    data = request.get_json() or {}
    for field in ("name", "description", "color", "is_final", "order", "is_active"):
        if field in data:
            setattr(status, field, data[field])
    return jsonify(repo.save(status).to_dict()), 200


@status_bp.route("/<int:status_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_status(status_id):
    status = repo.find_by_id(status_id)
    if not status:
        return jsonify({"error": "Status não encontrado"}), 404
    repo.delete(status)
    return jsonify({"message": "Status removido"}), 200
