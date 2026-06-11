"""Blueprint de autenticação — login, refresh token e dados do usuário logado."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpdesk.services.auth_service import AuthService
from helpdesk.models.user import User

auth_bp = Blueprint("auth", __name__)
service = AuthService()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica com email+senha e retorna access_token + refresh_token."""
    data = request.get_json() or {}
    result = service.authenticate(
        email=data.get("email"),
        password=data.get("password"),
    )
    return jsonify(result), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Troca refresh_token por um novo access_token."""
    identity = get_jwt_identity()
    result = service.refresh(identity)
    return jsonify(result), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retorna os dados do usuário atualmente autenticado."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(user.to_dict()), 200
