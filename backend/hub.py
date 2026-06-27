from core.db.base import AbstractDatabase
from core.services.user_service import UserService
from core.services.note_service import NoteService


class Hub:
    def __init__(self, database: AbstractDatabase):
        self.database = database
        self.user_service = UserService(database)
        self.note_service = NoteService(database)