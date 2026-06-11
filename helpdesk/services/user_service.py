from helpdesk.models.user import User
from helpdesk.repositories.user_repository import UserRepository
from helpdesk.utils.errors import ValidationError, NotFoundError


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def create(self, data):
        if not data.get("name") or not data.get("email"):
            raise ValidationError("Nome e email são obrigatórios")
        if not data.get("password"):
            raise ValidationError("Senha é obrigatória")
        if self.repo.find_by_email(data["email"]):
            raise ValidationError("Email já cadastrado")
        user = User(
            name=data["name"],
            email=data["email"],
            role=data.get("role", "client"),
            phone=data.get("phone"),
            company_id=data.get("company_id"),
        )
        user.set_password(data["password"])
        return self.repo.save(user)

    def get_by_id(self, user_id):
        user = self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário")
        return user

    def update(self, user_id, data):
        user = self.get_by_id(user_id)
        for field in ("name", "email", "role", "phone", "is_active", "company_id"):
            if field in data:
                setattr(user, field, data[field])
        if data.get("password"):
            user.set_password(data["password"])
        return self.repo.save(user)

    def delete(self, user_id):
        user = self.get_by_id(user_id)
        self.repo.delete(user)

    def list_users(self, page=1, per_page=20, **filters):
        return self.repo.paginate(page=page, per_page=per_page, **filters)
