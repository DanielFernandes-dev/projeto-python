from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.models.priority import Priority
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.decorators import role_required
from helpdesk.utils.extensions import db

priority_bp = Blueprint("priorities", __name__)
repo = BaseRepository(Priority)


@priority_bp.route("", methods=["GET"])
def list_priorities():
    priorities = Priority.query.filter_by(is_active=True).order_by(Priority.level).all()
    return jsonify({"priorities": [p.to_dict() for p in priorities]}), 200


@priority_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_priority():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 422
    priority = Priority(
        name=data["name"],
        level=data.get("level", 0),
        color=data.get("color", "#808080"),
    )
    return jsonify(repo.save(priority).to_dict()), 201


@priority_bp.route("/<int:priority_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_priority(priority_id):
    priority = repo.find_by_id(priority_id)
    if not priority:
        return jsonify({"error": "Prioridade não encontrada"}), 404
    data = request.get_json() or {}
    for field in ("name", "level", "color", "is_active"):
        if field in data:
            setattr(priority, field, data[field])
    return jsonify(repo.save(priority).to_dict()), 200


@priority_bp.route("/<int:priority_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_priority(priority_id):
    priority = repo.find_by_id(priority_id)
    if not priority:
        return jsonify({"error": "Prioridade não encontrada"}), 404
    repo.delete(priority)
    return jsonify({"message": "Prioridade removida"}), 200
