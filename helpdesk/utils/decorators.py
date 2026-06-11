from functools import wraps
from flask_jwt_extended import get_jwt_identity
from helpdesk.models import User
from helpdesk.utils.errors import ForbiddenError, UnauthorizedError


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UnauthorizedError("Usuário não autenticado")
            if user.role not in roles:
                raise ForbiddenError(
                    f"Acesso restrito para: {', '.join(roles)}"
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
