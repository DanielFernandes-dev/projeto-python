from datetime import datetime
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import SerializableMixin


class BaseModel(SerializableMixin, db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
