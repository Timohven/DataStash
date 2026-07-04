from datetime import datetime
from pydantic import BaseModel


class NoteCreate(BaseModel):
    note_type: str
    note_text: str


class NoteUpdate(BaseModel):
    note_type: str
    note_text: str


class NoteResponse(BaseModel):
    note_id: int
    author: str
    note_type: str
    text: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True  # строит модель из Note-объекта (не только из dict)