from fastapi import FastAPI

from app.api.v1.endpoints import auth, health
from app.db.base import Base
from app.db.session import engine

app = FastAPI()
Base.metadata.create_all(engine)

app.include_router(health.router)
app.include_router(auth.router)
