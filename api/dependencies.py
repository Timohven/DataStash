"""
api/dependencies.py

Сборка Hub один раз на процесс (через lru_cache — аналог
@st.cache_resource из Streamlit, но для обычных функций).
"""
import os
from functools import lru_cache

from sqlalchemy import create_engine

from core.hub import Hub
from core.db.sqlalchemy_db import Database


@lru_cache
def get_hub() -> Hub:
    engine = create_engine(
        os.environ["DATABASE_URL"],
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=10,
        max_overflow=20,
    )
    database = Database(engine=engine)
    return Hub(database=database)