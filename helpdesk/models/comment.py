from datetime import datetime
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import dt_iso


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    is_solution = db.Column(db.Boolean, default=False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "is_internal": self.is_internal,
            "is_solution": self.is_solution,
            "ticket_id": self.ticket_id,
            "author": self.author.name if self.author else None,
            "author_id": self.author_id,
            "created_at": dt_iso(self.created_at),
            "updated_at": dt_iso(self.updated_at),
        }
