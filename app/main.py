from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
