"""Serviço de tickets — CRUD, atribuição, comentários e filtros.

Centraliza toda a lógica de negócio relacionada a chamados,
isolando os resources (camada HTTP) dos models (camada de dados).
"""
from datetime import datetime
from helpdesk.models.ticket import Ticket
from helpdesk.models.comment import Comment
from helpdesk.models.status import Status
from helpdesk.models.user import User
from helpdesk.utils.extensions import db, db_save, db_delete
from helpdesk.exceptions import NotFoundError, ValidationError
from helpdesk.utils.helpers import gerar_protocolo, get_or_404, update_from_dict, apply_filters, pagination_response


class TicketService:
    def create(self, data, user_id):
        """Cria um novo ticket com protocolo único e persiste no banco."""
        protocol = gerar_protocolo()
        while Ticket.query.filter_by(protocol=protocol).first():
            protocol = gerar_protocolo()

        ticket = Ticket(
            title=data["title"],
            description=data["description"],
            protocol=protocol,
            created_by_id=user_id,
            company_id=data.get("company_id"),
            category_id=data.get("category_id"),
            priority_id=data.get("priority_id"),
            status_id=data.get("status_id"),
        )
        return db_save(ticket)

    def get_by_id(self, ticket_id):
        """Retorna ticket por ID ou levanta NotFoundError."""
        return get_or_404(Ticket, ticket_id, "Ticket")

    def get_by_protocol(self, protocol):
        """Retorna ticket por protocolo ou levanta NotFoundError."""
        ticket = Ticket.query.filter_by(protocol=protocol).first()
        if not ticket:
            raise NotFoundError("Ticket")
        return ticket

    def update(self, ticket_id, data):
        """Atualiza campos permitidos de um ticket.

        Se o status for final, define automaticamente a data de fechamento.
        """
        ticket = self.get_by_id(ticket_id)
        update_from_dict(ticket, data, (
            "title", "description", "category_id", "priority_id",
            "status_id", "assigned_to_id", "company_id",
        ))
        if "status_id" in data:
            status = Status.query.get(data["status_id"])
            if status and status.is_final:
                ticket.closed_at = datetime.utcnow()
        db.session.commit()
        return ticket

    def delete(self, ticket_id):
        """Remove um ticket do banco."""
        ticket = self.get_by_id(ticket_id)
        db_delete(ticket)

    def assign(self, ticket_id, technician_id):
        """Atribui um técnico (admin ou technician) a um ticket."""
        technician = User.query.get(technician_id)
        if not technician or technician.role not in ("admin", "technician"):
            raise ValidationError("Técnico inválido")
        ticket = self.get_by_id(ticket_id)
        ticket.assigned_to_id = technician_id
        db.session.commit()
        return ticket

    def add_comment(self, ticket_id, data, user_id):
        """Adiciona comentário a um ticket. Se marcado como solução,
        atualiza o status do ticket para 'Resolvido'."""
        ticket = self.get_by_id(ticket_id)
        comment = Comment(
            content=data["content"],
            is_internal=data.get("is_internal", False),
            is_solution=data.get("is_solution", False),
            ticket_id=ticket_id,
            author_id=user_id,
        )
        if data.get("is_solution"):
            resolved = Status.query.filter_by(name="Resolvido").first()
            if resolved:
                ticket.status_id = resolved.id
        db.session.add(comment)
        db.session.commit()
        return comment

    def list_tickets(self, page=1, per_page=20, **filters):
        """Lista tickets com paginação e filtros opcionais por coluna."""
        query = apply_filters(Ticket.query, Ticket, filters)
        return pagination_response(
            query.order_by(Ticket.id.desc()),
            page=page, per_page=per_page,
            items_key="tickets"
        )
