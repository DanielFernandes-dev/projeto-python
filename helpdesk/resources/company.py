from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.models.company import Company
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.decorators import role_required

company_bp = Blueprint("companies", __name__)
repo = BaseRepository(Company)


@company_bp.route("", methods=["GET"])
@jwt_required()
def list_companies():
    companies = Company.query.filter_by(is_active=True).all()
    return jsonify({"companies": [c.to_dict() for c in companies]}), 200


@company_bp.route("", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_company():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 422
    company = Company(
        name=data["name"],
        cnpj=data.get("cnpj"),
        email=data.get("email"),
        phone=data.get("phone"),
    )
    return jsonify(repo.save(company).to_dict()), 201


@company_bp.route("/<int:company_id>", methods=["GET"])
@jwt_required()
def get_company(company_id):
    company = repo.find_by_id(company_id)
    if not company:
        return jsonify({"error": "Empresa não encontrada"}), 404
    return jsonify(company.to_dict()), 200


@company_bp.route("/<int:company_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_company(company_id):
    company = repo.find_by_id(company_id)
    if not company:
        return jsonify({"error": "Empresa não encontrada"}), 404
    data = request.get_json() or {}
    for field in ("name", "cnpj", "email", "phone", "is_active"):
        if field in data:
            setattr(company, field, data[field])
    return jsonify(repo.save(company).to_dict()), 200


@company_bp.route("/<int:company_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_company(company_id):
    company = repo.find_by_id(company_id)
    if not company:
        return jsonify({"error": "Empresa não encontrada"}), 404
    repo.delete(company)
    return jsonify({"message": "Empresa removida"}), 200
