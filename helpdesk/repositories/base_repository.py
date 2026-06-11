from abc import ABC, abstractmethod
from helpdesk.utils.extensions import db


class BaseRepository(ABC):
    def __init__(self, model):
        self.model = model

    def find_all(self, **filters):
        query = self.model.query
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def find_by_id(self, entity_id):
        return self.model.query.get(entity_id)

    def save(self, entity):
        db.session.add(entity)
        db.session.commit()
        return entity

    def delete(self, entity):
        db.session.delete(entity)
        db.session.commit()

    def paginate(self, page=1, per_page=20, **filters):
        query = self.model.query
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        pagination = query.order_by(self.model.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return {
            "items": pagination.items,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
        }
