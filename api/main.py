"""
api/main.py

Точка входа FastAPI-приложения.

Запуск (из корня проекта, рядом с папками core/ и api/):
    uvicorn api.main:app --reload --port 8000

Документация автоматически будет доступна на:
    http://localhost:8000/docs
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, notes

app = FastAPI(title="DataStash API")

# CORS — пока разрешаем всё (* ), сузить под конкретные домены при выходе в прод
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/health")
def health():
    return {"status": "ok"}