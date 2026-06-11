"""Serviço de usuários — CRUD com validações de negócio.

Gerencia criação, atualização, listagem e remoção de usuários,
incluindo hash de senha e verificação de unicidade de email.
"""
from helpdesk.models.user import User
from helpdesk.utils.extensions import db, db_save, db_delete
from helpdesk.exceptions import ValidationError
from helpdesk.utils.helpers import get_or_404, update_from_dict, apply_filters, pagination_response


class UserService:
    def create(self, data):
        """Cria um novo usuário com senha hasheada.

        Valida presença de nome, email e senha, e unicidade do email.
        """
        if not data.get("name") or not data.get("email"):
            raise ValidationError("Nome e email são obrigatórios")
        if not data.get("password"):
            raise ValidationError("Senha é obrigatória")
        if User.query.filter_by(email=data["email"]).first():
            raise ValidationError("Email já cadastrado")
        user = User(
            name=data["name"],
            email=data["email"],
            role=data.get("role", "client"),
            phone=data.get("phone"),
            company_id=data.get("company_id"),
        )
        user.set_password(data["password"])
        return db_save(user)

    def get_by_id(self, user_id):
        """Retorna usuário por ID ou levanta NotFoundError."""
        return get_or_404(User, user_id, "Usuário")

    def update(self, user_id, data):
        """Atualiza campos permitidos de um usuário.

        Se a chave 'password' estiver presente, faz o hash da nova senha.
        """
        user = self.get_by_id(user_id)
        update_from_dict(user, data, (
            "name", "email", "role", "phone", "is_active", "company_id",
        ))
        if data.get("password"):
            user.set_password(data["password"])
        db.session.commit()
        return user

    def delete(self, user_id):
        """Remove um usuário do banco."""
        user = self.get_by_id(user_id)
        db_delete(user)

    def list_users(self, page=1, per_page=20, **filters):
        """Lista usuários com paginação e filtros opcionais (role, is_active)."""
        query = apply_filters(User.query, User, filters)
        return pagination_response(
            query.order_by(User.id.desc()),
            page=page, per_page=per_page,
            items_key="users"
        )
