# api/routers/tags.py
from fastapi import APIRouter, Depends
from api.dependencies import get_hub
from api.middleware.auth import get_current_username
from api.schemas.tag import TagResponse, NoteTagsUpdate
from core.hub import Hub

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
def get_all_tags(
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    return hub.tag_service.get_all_tags()


@router.get("/note/{note_id}", response_model=list[TagResponse])
def get_note_tags(
    note_id: int,
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    return hub.tag_service.get_tags_for_note(note_id)


@router.put("/note/{note_id}", response_model=list[TagResponse])
def set_note_tags(
    note_id: int,
    payload: NoteTagsUpdate,
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    return hub.tag_service.set_tags_for_note(note_id, payload.tag_names)
