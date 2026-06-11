from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Status(BaseModel):
    __tablename__ = "statuses"

    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(7), nullable=True, default="#808080")
    is_final = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)

    tickets = db.relationship("Ticket", backref="status", lazy="dynamic")
