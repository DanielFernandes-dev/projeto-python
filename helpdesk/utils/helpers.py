"""Funções utilitárias reutilizadas por serviços e recursos.

Inclui serialização, geração de protocolo, paginação, e atalhos
para operações comuns como get_or_404 e parse_pagination.
"""
from datetime import datetime
import random
import string
from flask import request
from helpdesk.exceptions import NotFoundError


def dt_iso(dt):
    """Converte datetime para string ISO 8601, ou None se receber None."""
    return dt.isoformat() if dt else None


def gerar_protocolo():
    """Gera um protocolo único no formato HD + 10 caracteres alfanuméricos."""
    return "HD" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def pagination_response(query, page=1, per_page=20, items_key="items"):
    """Executa a paginação de uma query SQLAlchemy e retorna dict padronizado.

    Args:
        query: Query SQLAlchemy já filtrada (sem order_by).
        page: Número da página (começa em 1).
        per_page: Itens por página.
        items_key: Chave do JSON que conterá a lista de itens.
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        items_key: [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }


def get_or_404(model, entity_id, name="Recurso"):
    """Busca por ID ou levanta NotFoundError — elimina try/except repetitivo."""
    obj = model.query.get(entity_id)
    if not obj:
        raise NotFoundError(name)
    return obj


def parse_pagination():
    """Extrai page e per_page dos query params da request (padrão 1 e 20)."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    return page, per_page


def update_from_dict(obj, data, fields):
    """Atribui seletivamente campos de um dict a um objeto via setattr.

    Só modifica os campos listados em 'fields' que existirem em 'data'.
    """
    for field in fields:
        if field in data:
            setattr(obj, field, data[field])


def apply_filters(query, model, filters):
    """Aplica filtros opcionais (chave=valor) a uma query, ignorando None."""
    for key, value in filters.items():
        if value is not None:
            query = query.filter(getattr(model, key) == value)
    return query
