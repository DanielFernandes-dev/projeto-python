from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import dt_iso


class User(db.Model):
    __tablename__ = "users"

    ROLES = ("admin", "technician", "client")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tickets_created = db.relationship(
        "Ticket", foreign_keys="Ticket.created_by_id", backref="creator", lazy="dynamic"
    )
    tickets_assigned = db.relationship(
        "Ticket", foreign_keys="Ticket.assigned_to_id", backref="assignee", lazy="dynamic"
    )
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "is_active": self.is_active,
            "company_id": self.company_id,
            "created_at": dt_iso(self.created_at),
            "updated_at": dt_iso(self.updated_at),
        }
