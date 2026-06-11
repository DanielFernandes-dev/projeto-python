"""Modelo Comment — comentário em um ticket, podendo ser interno ou solução."""
from datetime import datetime
from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Comment(BaseModel):
    __tablename__ = "comments"

    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    is_solution = db.Column(db.Boolean, default=False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def _extra_serialize(self):
        return {
            "author": self.author.name if self.author else None,
        }
