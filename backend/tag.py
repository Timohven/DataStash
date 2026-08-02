# core/models/tag.py
from dataclasses import dataclass

@dataclass
class Tag:
    tag_id: int
    name: str