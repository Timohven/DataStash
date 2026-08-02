# api/schemas/tag.py
from pydantic import BaseModel

class TagResponse(BaseModel):
    tag_id: int
    name: str

class NoteTagsUpdate(BaseModel):
    tag_names: list[str]  # ["работа", "важное", "личное"]
