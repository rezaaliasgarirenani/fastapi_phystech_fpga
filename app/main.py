"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.database import SessionLocal, init_db
from app.routers import auth, devices, missions, recommendations, users, vendors
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create the SQLite database and add example data on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Radiation-Resistant FPGA Selection API",
    description=(
        "Educational REST service for selecting radiation-resistant FPGA devices "
        "for space missions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vendors.router)
app.include_router(devices.router)
app.include_router(missions.router)
app.include_router(recommendations.router)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Basic health endpoint."""
    return {"status": "ok", "service": "fpga-selection-api"}
