from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.decorators import role_required


def create_crud_blueprint(
    name, import_name, model,
    list_order_attr=None,
    list_auth=False,
    get_by_id=False,
    create_fields=None,
    update_fields=None,
):
    if create_fields is None:
        create_fields = ["name"]
    if update_fields is None:
        update_fields = ["name"]

    bp = Blueprint(name, import_name)
    repo = BaseRepository(model)

    list_decorators = [jwt_required()] if list_auth else []

    @bp.route("", methods=["GET"], endpoint="list")
    def list_items():
        query = model.query.filter_by(is_active=True)
        if list_order_attr is not None:
            query = query.order_by(list_order_attr)
        items = query.all()
        return jsonify({name: [i.to_dict() for i in items]}), 200

    if list_decorators:
        for dec in reversed(list_decorators):
            list_items = dec(list_items)

    @bp.route("", methods=["POST"], endpoint="create")
    @jwt_required()
    @role_required("admin")
    def create_item():
        data = request.get_json() or {}
        if not data.get("name"):
            return jsonify({"error": "Nome é obrigatório"}), 422
        kwargs = {field: data.get(field) for field in create_fields if field != "name"}
        kwargs["name"] = data["name"]
        item = model(**kwargs)
        return jsonify(repo.save(item).to_dict()), 201

    @bp.route("/<int:item_id>", methods=["PUT"], endpoint="update")
    @jwt_required()
    @role_required("admin")
    def update_item(item_id):
        item = repo.find_by_id(item_id)
        if not item:
            return jsonify({"error": f"{model.__name__} não encontrado(a)"}), 404
        data = request.get_json() or {}
        for field in update_fields:
            if field in data:
                setattr(item, field, data[field])
        return jsonify(repo.save(item).to_dict()), 200

    @bp.route("/<int:item_id>", methods=["DELETE"], endpoint="delete")
    @jwt_required()
    @role_required("admin")
    def delete_item(item_id):
        item = repo.find_by_id(item_id)
        if not item:
            return jsonify({"error": f"{model.__name__} não encontrado(a)"}), 404
        repo.delete(item)
        return jsonify({"message": f"{model.__name__} removido(a)"}), 200

    if get_by_id:
        @bp.route("/<int:item_id>", methods=["GET"], endpoint="get")
        @jwt_required()
        def get_item(item_id):
            item = repo.find_by_id(item_id)
            if not item:
                return jsonify({"error": f"{model.__name__} não encontrado(a)"}), 404
            return jsonify(item.to_dict()), 200

    return bp
