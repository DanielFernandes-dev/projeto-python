"""Configurações da aplicação — lê do .env com fallbacks para desenvolvimento.

As chaves SECRET_KEY e JWT_SECRET_KEY usam valores fixos apenas quando
não há arquivo .env (ambiente de desenvolvimento local).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "helpdesk-pro-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///helpdesk.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True
