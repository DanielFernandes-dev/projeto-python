"""Popula o banco com dados iniciais para desenvolvimento.

Cria 3 usuários (admin, técnico, cliente), 6 status, 4 prioridades
e 6 categorias. Executar com: python seed.py
"""
from app import create_app
from helpdesk.utils.extensions import db
from helpdesk.models.user import User
from helpdesk.models.status import Status
from helpdesk.models.priority import Priority
from helpdesk.models.category import Category


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.first():
            print("Banco já contém dados. Seed ignorado.")
            return

        admin = User(
            name="Administrador",
            email="admin@helpdesk.com",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

        tech = User(
            name="Técnico Suporte",
            email="tecnico@helpdesk.com",
            role="technician",
        )
        tech.set_password("tec123")
        db.session.add(tech)

        client = User(
            name="Cliente Teste",
            email="cliente@helpdesk.com",
            role="client",
        )
        client.set_password("cli123")
        db.session.add(client)

        statuses = [
            Status(name="Aberto", color="#3498db", order=1),
            Status(name="Em Andamento", color="#f39c12", order=2),
            Status(name="Aguardando Cliente", color="#e67e22", order=3),
            Status(name="Resolvido", color="#2ecc71", is_final=True, order=4),
            Status(name="Fechado", color="#95a5a6", is_final=True, order=5),
            Status(name="Cancelado", color="#e74c3c", is_final=True, order=6),
        ]
        db.session.add_all(statuses)

        priorities = [
            Priority(name="Baixa", level=1, color="#2ecc71"),
            Priority(name="Média", level=2, color="#f39c12"),
            Priority(name="Alta", level=3, color="#e74c3c"),
            Priority(name="Crítica", level=4, color="#9b59b6"),
        ]
        db.session.add_all(priorities)

        categories = [
            Category(name="Hardware", description="Problemas com equipamentos físicos"),
            Category(name="Software", description="Problemas com programas e sistemas"),
            Category(name="Rede", description="Problemas de conectividade e rede"),
            Category(name="Email", description="Problemas com correio eletrônico"),
            Category(name="Acesso", description="Problemas de acesso e permissões"),
            Category(name="Outros", description="Outros tipos de solicitação"),
        ]
        db.session.add_all(categories)

        db.session.commit()
        print("Seed concluído com sucesso!")
        print()
        print("Credenciais de acesso:")
        print("  Admin:    admin@helpdesk.com / admin123")
        print("  Técnico:  tecnico@helpdesk.com / tec123")
        print("  Cliente:  cliente@helpdesk.com / cli123")


if __name__ == "__main__":
    seed()
