import os
from contextlib import asynccontextmanager
from time import monotonic
from fastapi import FastAPI
from app.api.routes import router
from app.ml.inference import ModelLoader
from app.repositories.audit import AuditRepository

@asynccontextmanager
async def lifespan(app):
    app.state.started = monotonic()
    app.state.model = ModelLoader()
    app.state.audit = AuditRepository(os.getenv("DB_PATH", "runtime/audit.db"))
    yield

app = FastAPI(title="Smart Helpdesk", lifespan=lifespan)
app.include_router(router)
