# api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import get_hub
from api.middleware.auth import create_access_token
from api.schemas.auth import TokenResponse
from core.hub import Hub

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),  # ← читает form data
    hub: Hub = Depends(get_hub),
):
    user = hub.user_service.get_authenticated_user(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(username=form.username)
    return TokenResponse(access_token=token)