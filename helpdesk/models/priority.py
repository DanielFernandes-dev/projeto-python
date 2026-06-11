from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Priority(BaseModel):
    __tablename__ = "priorities"

    name = db.Column(db.String(50), nullable=False, unique=True)
    level = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String(7), nullable=True, default="#808080")
    is_active = db.Column(db.Boolean, default=True)

    tickets = db.relationship("Ticket", backref="priority", lazy="dynamic")
