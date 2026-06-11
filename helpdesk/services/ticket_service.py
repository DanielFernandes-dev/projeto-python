from datetime import datetime
from helpdesk.models.ticket import Ticket
from helpdesk.models.comment import Comment
from helpdesk.models.status import Status
from helpdesk.repositories.ticket_repository import TicketRepository
from helpdesk.repositories.user_repository import UserRepository
from helpdesk.utils.extensions import db
from helpdesk.exceptions import NotFoundError, ValidationError
from helpdesk.utils.helpers import gerar_protocolo


class TicketService:
    def __init__(self):
        self.repo = TicketRepository()
        self.user_repo = UserRepository()

    def create(self, data, user_id):
        protocol = gerar_protocolo()
        while self.repo.find_by_protocol(protocol):
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
        return self.repo.save(ticket)

    def get_by_id(self, ticket_id):
        ticket = self.repo.find_by_id(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket")
        return ticket

    def get_by_protocol(self, protocol):
        ticket = self.repo.find_by_protocol(protocol)
        if not ticket:
            raise NotFoundError("Ticket")
        return ticket

    def update(self, ticket_id, data):
        ticket = self.get_by_id(ticket_id)
        for field in ("title", "description", "category_id", "priority_id",
                      "status_id", "assigned_to_id", "company_id"):
            if field in data:
                setattr(ticket, field, data[field])
        if "status_id" in data:
            status = Status.query.get(data["status_id"])
            if status and status.is_final:
                ticket.closed_at = datetime.utcnow()
        return self.repo.save(ticket)

    def delete(self, ticket_id):
        ticket = self.get_by_id(ticket_id)
        self.repo.delete(ticket)

    def assign(self, ticket_id, technician_id):
        technician = self.user_repo.find_by_id(technician_id)
        if not technician or technician.role not in ("admin", "technician"):
            raise ValidationError("Técnico inválido")
        ticket = self.get_by_id(ticket_id)
        ticket.assigned_to_id = technician_id
        return self.repo.save(ticket)

    def add_comment(self, ticket_id, data, user_id):
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
        return self.repo.paginate(page=page, per_page=per_page, **filters)
