"""
api/middleware/auth.py

Минимальная JWT-аутентификация с нуля:
  - create_access_token(username) -> str          — создать токен после логина
  - get_current_username(token) -> str             — FastAPI dependency, проверяет токен

Алгоритм: HS256 (симметричный, секрет общий, без приватного/публичного ключа —
этого достаточно для одного бэкенда; если бэкендов будет несколько отдельных
сервисов, проверяющих токены независимо, стоит перейти на RS256).
"""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа — удобно для мобильного клиента

# Указывает FastAPI/Swagger, что токен ожидается в заголовке Authorization: Bearer <token>,
# а получить его можно через POST /auth/login (для автодокументации /docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency: достаёт username из JWT-токена.
    Используется в роутерах как: user=Depends(get_current_username)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception