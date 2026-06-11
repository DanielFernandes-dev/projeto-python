from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.services.user_service import UserService
from helpdesk.utils.decorators import role_required
from helpdesk.utils.helpers import pagination_response

user_bp = Blueprint("users", __name__)
service = UserService()


@user_bp.route("", methods=["GET"])
@jwt_required()
@role_required("admin", "technician")
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    is_active = request.args.get("is_active")
    if is_active is not None:
        is_active = is_active.lower() == "true"
    result = service.list_users(
        page=page, per_page=per_page,
        role=role, is_active=is_active,
    )
    return jsonify(pagination_response(result, "users")), 200


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = service.get_by_id(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    user = service.create(data)
    return jsonify(user.to_dict()), 201


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}
    user = service.update(user_id, data)
    return jsonify(user.to_dict()), 200


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    service.delete(user_id)
    return jsonify({"message": "Usuário removido"}), 200
