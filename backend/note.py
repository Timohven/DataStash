from dataclasses import dataclass


@dataclass
class Note:
    note_id: int
    created_at: str
    author: str
    note_type: str
    text: str