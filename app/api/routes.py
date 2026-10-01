from time import monotonic
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import generate_latest, CONTENT_TYPE_LATEST
from app.api.schemas import PredictionRequest, PredictionResponse, HealthResponse
from app.core.security import require_key
from app.services.prediction import Predictor
from app.ml.errors import ModelUnavailableError

router = APIRouter(dependencies=[Depends(require_key)])

@router.post("/api/v1/predict", response_model=PredictionResponse)
def predict(body: PredictionRequest, request: Request):
    try:
        result = Predictor(request.app.state.model).predict(body)
    except ModelUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    request.app.state.audit.save(result)
    return result

@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    state = request.app.state
    db_ready = state.audit.ready()
    ready = state.model.loaded and db_ready
    result = HealthResponse(
        status="healthy" if ready else "not_ready",
        model_loaded=state.model.loaded, database_ready=db_ready,
        model_version=state.model.version,
        uptime_seconds=monotonic()-state.started)
    return JSONResponse(result.model_dump(), status_code=200 if ready else 503)

@router.get("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
