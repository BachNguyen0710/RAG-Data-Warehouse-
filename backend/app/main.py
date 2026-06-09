from fastapi import FastAPI
from backend.app.core.config import settings

app = FastAPI(
    title= settings.PROJECT_NAME,
    version = "1.0.0"
              )

@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}