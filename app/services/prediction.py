from typing import Protocol
from uuid import uuid4
from app.ml.errors import ModelUnavailableError
from app.schemas import ModelPrediction, PredictionRequest, PredictionResponse

ROUTES = {"ACCOUNT": "IT", "STUDY": "DEAN_OFFICE",
          "PAYMENT": "FINANCE", "OTHER": "OPERATOR"}

def choose_route(category: str, confidence: float):
    manual = confidence < 0.8 or category == "OTHER"
    return ("OPERATOR" if manual else ROUTES[category]), manual

class Model(Protocol):
    loaded: bool
    version: str | None
    def predict(self, text: str) -> tuple[str, float]: ...

class Predictor:
    def __init__(self, model: Model):
        self.model = model

    def predict(self, request: PredictionRequest | dict) -> PredictionResponse:
        # Повторная проверка защищает и от измененного объекта Pydantic.
        data = request.model_dump() if isinstance(request, PredictionRequest) else request
        request = PredictionRequest.model_validate(data)
        if not self.model.loaded:
            raise ModelUnavailableError("MODEL_NOT_READY")
        try:
            category, confidence = self.model.predict(request.text)
            prediction = ModelPrediction(category=category, confidence=confidence)
            route, manual = choose_route(prediction.category, prediction.confidence)
            return PredictionResponse(
                request_id=uuid4(), item_id=request.item_id,
                prediction=prediction.category, confidence=prediction.confidence,
                route=route, model_version=self.model.version,
                manual_review_required=manual,
            )
        except ModelUnavailableError:
            raise
        except Exception as exc:
            raise ModelUnavailableError("MODEL_INFERENCE_FAILED") from exc
