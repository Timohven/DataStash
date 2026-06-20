from backend.database import Database
from backend.user_service import UserService
from backend.note_service import NoteService


class Hub:
    def __init__(self):
        database = Database()
        self.user_service = UserService(database)
        self.note_service = NoteService(database)