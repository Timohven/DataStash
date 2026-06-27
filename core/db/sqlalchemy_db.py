from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from core.db.base import AbstractDatabase


class Database(AbstractDatabase):
    def __init__(self, engine: Engine):
        self.engine = engine

    def execute_query(self, query: str, params: dict = None, write: bool = False):
        params = params or {}
        if write:
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params)
                try:
                    return result.fetchall()
                except Exception:
                    return result
        else:
            with self.engine.connect() as conn:
                return conn.execute(text(query), params).fetchall()

    def dispose(self):
        self.engine.dispose()