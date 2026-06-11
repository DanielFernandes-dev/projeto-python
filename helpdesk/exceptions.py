"""Hierarquia de exceções da aplicação e handlers globais do Flask.

Todas as exceções herdam de AppError (message + status_code), o que
permite o errorhandler genérico retornar JSON padronizado em vez de
HTML nas respostas de erro.
"""
from flask import jsonify


class AppError(Exception):
    """Exceção base — carrega mensagem amigável e código HTTP."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """Recurso solicitado não existe (404)."""
    def __init__(self, entity="Recurso"):
        super().__init__(f"{entity} não encontrado(a)", 404)


class ValidationError(AppError):
    """Dados enviados pelo cliente são inválidos (422)."""
    def __init__(self, message="Dados inválidos"):
        super().__init__(message, 422)


class UnauthorizedError(AppError):
    """Credenciais ausentes ou inválidas (401)."""
    def __init__(self, message="Acesso não autorizado"):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    """Usuário autenticado mas sem permissão para a ação (403)."""
    def __init__(self, message="Permissão negada"):
        super().__init__(message, 403)


def register_error_handlers(app):
    """Registra handlers globais que retornam JSON em vez de HTML."""
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(422)
    def handle_unprocessable(error):
        return jsonify({"error": "Entidade não processável"}), 422

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Erro interno do servidor"}), 500
