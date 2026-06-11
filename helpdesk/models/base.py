"""BaseModel — classe abstrata que todo model ORM estende.

Fornece:
  - Chave primária `id` (autoincremento)
  - Timestamp `created_at`
  - Método `to_dict()` para serialização automática das colunas
  - Hook `_extra_serialize()` para subclasses incluírem campos computados
"""
from datetime import datetime
from helpdesk.utils.extensions import db
from helpdesk.utils.helpers import dt_iso


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    serialize_exclude = set()

    def _extra_serialize(self):
        return {}

    def to_dict(self):
        data = {}
        for col in self.__table__.columns:
            if col.name in self.serialize_exclude:
                continue
            val = getattr(self, col.name)
            data[col.name] = dt_iso(val) if isinstance(val, datetime) else val
        data.update(self._extra_serialize())
        return data
