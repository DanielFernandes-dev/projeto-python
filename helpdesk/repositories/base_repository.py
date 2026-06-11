from helpdesk.utils.extensions import db


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def _apply_filters(self, query, **filters):
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query

    def find_all(self, **filters):
        return self._apply_filters(self.model.query, **filters).all()

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
        query = self._apply_filters(self.model.query, **filters)
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
