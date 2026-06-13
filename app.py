"""Fábrica da aplicação Flask — monta e retorna a instância do servidor.

Todos os blueprints (auth, users, tickets, etc.) são registrados aqui
com o prefixo /api. A criação das tabelas no banco é automática ao iniciar.
"""
from flask import Flask
from helpdesk.config import Config
from helpdesk.utils.extensions import db, jwt, ma
from helpdesk.exceptions import register_error_handlers
from helpdesk.resources.auth import auth_bp
from helpdesk.resources.user import user_bp
from helpdesk.resources.ticket import ticket_bp
from helpdesk.resources.category import category_bp
from helpdesk.resources.priority import priority_bp
from helpdesk.resources.status import status_bp
from helpdesk.resources.company import company_bp
from helpdesk.resources.dashboard import dashboard_bp
from helpdesk.resources.chamado import chamado_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    register_error_handlers(app)

    prefix = "/api"
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(user_bp, url_prefix=f"{prefix}/users")
    app.register_blueprint(ticket_bp, url_prefix=f"{prefix}/tickets")
    app.register_blueprint(category_bp, url_prefix=f"{prefix}/categories")
    app.register_blueprint(priority_bp, url_prefix=f"{prefix}/priorities")
    app.register_blueprint(status_bp, url_prefix=f"{prefix}/statuses")
    app.register_blueprint(company_bp, url_prefix=f"{prefix}/companies")
    app.register_blueprint(dashboard_bp, url_prefix=f"{prefix}/dashboard")
    app.register_blueprint(chamado_bp, url_prefix=f"{prefix}/chamados")

    @app.route("/")
    def index():
        return {
            "service": "HelpDesk Pro",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "auth": "/api/auth/login",
                "users": "/api/users",
                "tickets": "/api/tickets",
                "categories": "/api/categories",
                "priorities": "/api/priorities",
                "statuses": "/api/statuses",
                "companies": "/api/companies",
                "dashboard": "/api/dashboard",
            },
        }

    @app.route("/api/health")
    def health_check():
        return {"status": "ok", "service": "HelpDesk Pro"}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
