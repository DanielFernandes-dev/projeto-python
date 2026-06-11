from helpdesk.models.base import BaseModel
from helpdesk.utils.extensions import db


class Attachment(BaseModel):
    __tablename__ = "attachments"

    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    uploader = db.relationship("User")

    def _extra_serialize(self):
        return {
            "uploaded_by": self.uploader.name if self.uploader else None,
        }
