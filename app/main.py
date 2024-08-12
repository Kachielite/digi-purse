from fastapi import FastAPI

from app.api.v1.endpoints import auth
from app.db.base import Base
from app.db.session import engine

app = FastAPI()
Base.metadata.create_all(engine)


# Health Check
@app.get("/healthy")
def check_health():
    return {"status": "System Healthy"}


app.include_router(auth.router)
