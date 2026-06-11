"""Modelo TicketHistory — log de ações executadas em um chamado.

Cada entrada registra a ação (ex: "Status alterado para: resolvido")
e quem a executou, formando a trilha de auditoria do ticket.
"""
from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class TicketHistory(BaseModel):
    __tablename__ = "ticket_history"

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
    responsavel = db.Column(db.String(150), nullable=False)
