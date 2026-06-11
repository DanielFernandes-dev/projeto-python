from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.models.category import Category
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.decorators import role_required
from helpdesk.utils.extensions import db

category_bp = Blueprint("categories", __name__)
repo = BaseRepository(Category)


@category_bp.route("", methods=["GET"])
def list_categories():
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify({"categories": [c.to_dict() for c in categories]}), 200


@category_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_category():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 422
    category = Category(name=data["name"], description=data.get("description"))
    return jsonify(repo.save(category).to_dict()), 201


@category_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_category(category_id):
    category = repo.find_by_id(category_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    data = request.get_json() or {}
    for field in ("name", "description", "is_active"):
        if field in data:
            setattr(category, field, data[field])
    return jsonify(repo.save(category).to_dict()), 200


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_category(category_id):
    category = repo.find_by_id(category_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    repo.delete(category)
    return jsonify({"message": "Categoria removida"}), 200
