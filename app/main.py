from fastapi import FastAPI

from app.api.v1.endpoints import auth, health, user, wallet
from app.db.base import Base
from app.db.session import engine

app = FastAPI()
Base.metadata.create_all(engine)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(wallet.router)