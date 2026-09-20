from time import monotonic
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import REGISTRY
from prometheus_client.openmetrics.exposition import generate_latest, CONTENT_TYPE_LATEST
from app.api.schemas import PredictionRequest, PredictionResponse, HealthResponse
from app.core.security import require_key
from app.services.prediction import choose_route

router = APIRouter(dependencies=[Depends(require_key)])

@router.post("/api/v1/predict", response_model=PredictionResponse)
def predict(body: PredictionRequest, request: Request):
    model = request.app.state.model
    if not model.loaded:
        raise HTTPException(503, "MODEL_NOT_READY")
    category, confidence = model.predict(body.text)
    route, manual = choose_route(category, confidence)
    result = PredictionResponse(
        request_id=uuid4(), item_id=body.item_id,
        prediction=category, confidence=confidence, route=route,
        model_version=model.version, manual_review_required=manual)
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
