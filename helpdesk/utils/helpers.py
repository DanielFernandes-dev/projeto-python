def dt_iso(dt):
    return dt.isoformat() if dt else None


def pagination_response(paginated, items_key="items"):
    return {
        items_key: [item.to_dict() for item in paginated["items"]],
        "total": paginated["total"],
        "page": paginated["page"],
        "per_page": paginated["per_page"],
        "pages": paginated["pages"],
    }
