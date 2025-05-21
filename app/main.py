from fastapi import FastAPI

from app.routers.users import user_router
from app.routers.auth import auth_router

app = FastAPI()

app.include_router(user_router)
app.include_router(auth_router)