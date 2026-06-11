from helpdesk.models.ticket import Ticket
from helpdesk.models.status import Status
from helpdesk.repositories.base_repository import BaseRepository
from helpdesk.utils.extensions import db


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def find_by_protocol(self, protocol):
        return Ticket.query.filter_by(protocol=protocol).first()

    def find_by_creator(self, user_id, page=1, per_page=20):
        return self.paginate(page=page, per_page=per_page, created_by_id=user_id)

    def find_by_assignee(self, user_id, page=1, per_page=20):
        return self.paginate(page=page, per_page=per_page, assigned_to_id=user_id)

    def find_open_tickets(self, page=1, per_page=20):
        closed_statuses = Status.query.filter_by(is_final=True).all()
        closed_ids = [s.id for s in closed_statuses]
        if not closed_ids:
            return self.paginate(page=page, per_page=per_page)
        pagination = Ticket.query.filter(
            ~Ticket.status_id.in_(closed_ids)
        ).order_by(Ticket.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "items": pagination.items,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        }

    def _closed_ids(self):
        return [s.id for s in Status.query.filter_by(is_final=True).all()]

    def dashboard_stats(self):
        total = Ticket.query.count()
        closed_ids = self._closed_ids()
        open_count = Ticket.query.filter(~Ticket.status_id.in_(closed_ids)).count() if closed_ids else total
        closed_count = Ticket.query.filter(Ticket.status_id.in_(closed_ids)).count() if closed_ids else 0
        recent = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "recent": [t.to_dict() for t in recent],
        }
