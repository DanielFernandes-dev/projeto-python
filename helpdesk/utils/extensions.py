"""Singleton das extensões Flask e helpers de banco.

db, jwt e ma são inicializados sem app e vinculados depois via init_app().
db_save / db_delete eliminam a repetição de add+commit / delete+commit.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()


def db_save(obj):
    """Persiste um objeto no banco (add + commit) e o retorna."""
    db.session.add(obj)
    db.session.commit()
    return obj


def db_delete(obj):
    """Remove um objeto do banco (delete + commit)."""
    db.session.delete(obj)
    db.session.commit()
