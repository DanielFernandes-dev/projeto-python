from flask_jwt_extended import create_access_token, create_refresh_token
from helpdesk.repositories.user_repository import UserRepository
from helpdesk.utils.errors import UnauthorizedError, ValidationError


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate(self, email, password):
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")
        user = self.user_repo.find_by_email(email)
        if not user or not user.check_password(password):
            raise UnauthorizedError("Credenciais inválidas")
        if not user.is_active:
            raise UnauthorizedError("Usuário inativo")
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }

    def refresh(self, identity):
        access_token = create_access_token(identity=identity)
        return {"access_token": access_token}
