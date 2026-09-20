from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

Category = Literal["ACCOUNT", "STUDY", "PAYMENT", "OTHER"]

class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True
    )
    item_id: str = Field(
        strict=True, pattern=r"^TKT-[0-9]{1,10}$"
    )
    text: str = Field(strict=True, min_length=10, max_length=3000)

class PredictionResponse(BaseModel):
    request_id: UUID
    item_id: str
    prediction: Category
    confidence: float = Field(ge=0, le=1)
    route: Literal["IT", "DEAN_OFFICE", "FINANCE", "OPERATOR"]
    model_version: str
    manual_review_required: bool

class HealthResponse(BaseModel):
    status: Literal["healthy", "not_ready"]
    model_loaded: bool
    database_ready: bool
    model_version: str | None
    uptime_seconds: float = Field(ge=0)
