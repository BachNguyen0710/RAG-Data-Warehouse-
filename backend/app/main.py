from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import documents, chat, auth
from app.services.vector_db import ensure_collection

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

# Cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # địa chỉ Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(auth.router)

@app.on_event("startup")
def startup():
    ensure_collection()

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.PROJECT_NAME}