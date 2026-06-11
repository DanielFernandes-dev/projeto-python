from datetime import datetime
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import SerializableMixin


class TicketHistory(SerializableMixin, db.Model):
    __tablename__ = "ticket_history"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
    responsavel = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
