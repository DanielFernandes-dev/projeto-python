from datetime import datetime
import random
import string


def dt_iso(dt):
    return dt.isoformat() if dt else None


def gerar_protocolo():
    return "HD" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def pagination_response(paginated, items_key="items"):
    return {
        items_key: [item.to_dict() for item in paginated["items"]],
        "total": paginated["total"],
        "page": paginated["page"],
        "per_page": paginated["per_page"],
        "pages": paginated["pages"],
    }


class SerializableMixin:
    serialize_exclude = set()

    def _extra_serialize(self):
        return {}

    def to_dict(self):
        data = {}
        for col in self.__table__.columns:
            if col.name in self.serialize_exclude:
                continue
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                data[col.name] = dt_iso(val)
            else:
                data[col.name] = val
        data.update(self._extra_serialize())
        return data
