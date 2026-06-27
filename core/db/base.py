"""
core/db/base.py

Абстрактный интерфейс, который должна реализовывать любая Database.
NoteService и UserService технически от него не зависят напрямую
(duck typing), но он служит явным контрактом и страховкой от ошибок.
"""
from abc import ABC, abstractmethod
from typing import Any, Sequence


class AbstractDatabase(ABC):
    @abstractmethod
    def execute_query(
        self,
        query: str,
        params: dict | None = None,
        write: bool = False,
    ) -> Sequence[Any]:
        """
        Выполняет SQL-запрос.

        :param query: SQL-запрос (с именованными параметрами :name)
        :param params: словарь параметров для запроса
        :param write: True для INSERT/UPDATE/DELETE (с commit),
                       False для SELECT (без commit)
        :return: список строк результата (для SELECT и INSERT...RETURNING)
        """
        raise NotImplementedError

    @abstractmethod
    def dispose(self) -> None:
        """Закрывает пул соединений / освобождает ресурсы."""
        raise NotImplementedError