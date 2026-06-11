from datetime import datetime
from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Company(BaseModel):
    __tablename__ = "companies"

    name = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship("User", backref="company", lazy="dynamic")
    tickets = db.relationship("Ticket", backref="company", lazy="dynamic")
