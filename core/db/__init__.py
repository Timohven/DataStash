"""
core/db/__init__.py

Делает классы пакета доступными напрямую через core.db,
без необходимости знать внутреннюю структуру файлов.
"""
from core.db.base import AbstractDatabase
from core.db.sqlalchemy_db import Database

__all__ = ["AbstractDatabase", "Database"]