from datetime import datetime
from helpdesk.utils.extensions import db


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    protocol = db.Column(db.String(20), unique=True, nullable=False)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    priority_id = db.Column(db.Integer, db.ForeignKey("priorities.id"), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "protocol": self.protocol,
            "created_by": self.creator.name if self.creator else None,
            "created_by_id": self.created_by_id,
            "assigned_to": self.assignee.name if self.assignee else None,
            "assigned_to_id": self.assigned_to_id,
            "company_id": self.company_id,
            "category": self.category.name if self.category else None,
            "category_id": self.category_id,
            "priority": self.priority.name if self.priority else None,
            "priority_id": self.priority_id,
            "status": self.status.name if self.status else None,
            "status_id": self.status_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }
