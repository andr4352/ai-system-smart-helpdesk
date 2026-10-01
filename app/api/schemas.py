from typing import Literal
from pydantic import BaseModel, Field
from app.schemas import Category, PredictionRequest, PredictionResponse

class HealthResponse(BaseModel):
    status: Literal["healthy", "not_ready"]
    model_loaded: bool
    database_ready: bool
    model_version: str | None
    uptime_seconds: float = Field(ge=0)
