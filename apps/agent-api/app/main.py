from fastapi import FastAPI, HTTPException

from app.agents import chief_of_staff
from app.db import init_db

app = FastAPI(title="Jarvis Agent API")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run/good-morning")
def run_good_morning():
    try:
        return chief_of_staff.run_good_morning()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
