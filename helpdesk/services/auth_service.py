"""Serviço de autenticação — login, refresh e verificação de credenciais."""
from flask_jwt_extended import create_access_token, create_refresh_token
from helpdesk.models.user import User
from helpdesk.exceptions import UnauthorizedError, ValidationError


class AuthService:
    def authenticate(self, email, password):
        """Valida credenciais e retorna tokens JWT + dados do usuário."""
        if not email or not password:
            raise ValidationError("Email e senha são obrigatórios")
        user = User.query.filter_by(email=email).first()
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
        """Gera novo access_token a partir do refresh_token."""
        access_token = create_access_token(identity=identity)
        return {"access_token": access_token}
