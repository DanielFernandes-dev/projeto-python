"""Modelo Ticket — representa um chamado de suporte.

Cada ticket possui título, descrição, protocolo único, SLA em horas,
e relacionamentos com usuário criador, técnico responsável, empresa,
categoria, prioridade e status.

O histórico de ações é armazenado em TicketHistory.
"""
from datetime import datetime, timedelta
from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import dt_iso


class Ticket(BaseModel):
    __tablename__ = "tickets"

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    protocol = db.Column(db.String(20), unique=True, nullable=False)
    sla_horas = db.Column(db.Integer, nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    priority_id = db.Column(db.Integer, db.ForeignKey("priorities.id"), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    comments = db.relationship(
        "Comment", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Comment.created_at"
    )
    attachments = db.relationship(
        "Attachment", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    historico = db.relationship(
        "TicketHistory", backref="ticket", lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="TicketHistory.created_at"
    )

    def tempo_decorrido(self):
        """Timedelta desde a abertura do chamado."""
        return datetime.utcnow() - self.created_at

    def esta_em_atraso(self):
        """True se o chamado ultrapassou o SLA e não foi finalizado."""
        if not self.sla_horas or not self.status:
            return False
        if self.status.is_final:
            return False
        return self.tempo_decorrido() > timedelta(hours=self.sla_horas)

    def _extra_serialize(self):
        return {
            "cliente": self.creator.name if self.creator else None,
            "tecnico": self.assignee.name if self.assignee else None,
            "category": self.category.name if self.category else None,
            "priority": self.priority.name.lower() if self.priority else None,
            "status": self.status.name.lower() if self.status else None,
            "created_at": dt_iso(self.created_at),
            "updated_at": dt_iso(self.updated_at),
            "closed_at": dt_iso(self.closed_at),
            "historico": [h.to_dict() for h in self.historico.all()],
            "tempo_decorrido_horas": round(
                self.tempo_decorrido().total_seconds() / 3600, 2
            ),
            "em_atraso": self.esta_em_atraso(),
        }

    def __str__(self):
        decorrido = self.tempo_decorrido()
        horas = int(decorrido.total_seconds() // 3600)
        minutos = int((decorrido.total_seconds() % 3600) // 60)
        return (
            f"[#{self.id}] {self.title} | "
            f"Cliente: {self.creator.name if self.creator else 'N/A'} | "
            f"Prioridade: {self.priority.name.lower() if self.priority else 'N/A'} | "
            f"Status: {self.status.name.lower() if self.status else 'N/A'} | "
            f"Tempo: {horas}h{minutos:02d}min"
        )
