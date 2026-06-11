"""Modelo Category — categorias para classificar tickets (ex: Hardware, Rede)."""
from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    tickets = db.relationship("Ticket", backref="category", lazy="dynamic")
