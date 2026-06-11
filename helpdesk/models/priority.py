from datetime import datetime
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import SerializableMixin


class Priority(SerializableMixin, db.Model):
    __tablename__ = "priorities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    level = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String(7), nullable=True, default="#808080")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship("Ticket", backref="priority", lazy="dynamic")
