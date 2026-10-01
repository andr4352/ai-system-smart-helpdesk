import hashlib
import json
import pytest
from pydantic import ValidationError
from app.ml.errors import ModelUnavailableError
from app.ml.inference import ModelLoader
from app.ml.training import train
from app.schemas import PredictionRequest, PredictionResponse
from app.services.prediction import Predictor, choose_route

@pytest.fixture(scope="module")
def artifact(tmp_path_factory):
    return train(output_dir=tmp_path_factory.mktemp("model"))

@pytest.fixture(scope="module")
def predictor(artifact):
    return Predictor(ModelLoader(artifact))

def test_correct_request(predictor):
    result = predictor.predict({"item_id": "TKT-101", "text": "Не могу войти в свой личный кабинет"})
    assert isinstance(result, PredictionResponse)
    assert result.prediction == "ACCOUNT"
    assert result.route == "IT"
    assert not result.manual_review_required
    assert result.model_version == "helpdesk-tfidf-lr-1.0.0"
    assert result.item_id == "TKT-101"
    assert 0 <= result.confidence <= 1
    assert PredictionResponse.model_validate_json(result.model_dump_json()) == result

def test_second_topic(predictor):
    result = predictor.predict({"item_id": "TKT-102", "text": "Подскажите когда будет пересдача экзамена"})
    assert result.prediction == "STUDY"
    assert result.route == "OPERATOR"
    assert result.manual_review_required
    assert result.confidence < 0.8

def test_payment_topic(predictor):
    result = predictor.predict({"item_id": "TKT-103", "text": "Моя оплата за обучение не отобразилась"})
    assert result.prediction == "PAYMENT"
    assert result.route == "FINANCE"

def test_unclear_request(predictor):
    result = predictor.predict({"item_id": "TKT-104", "text": "Помогите пожалуйста разобраться"})
    assert result.confidence < 0.8
    assert result.manual_review_required
    assert result.route == "OPERATOR"

@pytest.mark.parametrize("patch", [
    {"text": ""}, {"text": " " * 20}, {"text": "а" * 9},
    {"text": "а" * 3001}, {"text": 123}, {"item_id": "bad"}, {"extra": 1},
])
def test_invalid_input(predictor, patch):
    with pytest.raises(ValidationError):
        predictor.predict({"item_id": "TKT-1", "text": "Нужна помощь с заявкой"} | patch)

@pytest.mark.parametrize("length", [10, 3000])
def test_inclusive_length_limits(predictor, length):
    request = PredictionRequest(item_id="TKT-1", text="а" * length)
    assert isinstance(predictor.predict(request), PredictionResponse)

def test_missing_model(tmp_path):
    model = ModelLoader(tmp_path / "missing.joblib")
    assert not model.loaded
    with pytest.raises(ModelUnavailableError, match="MODEL_NOT_READY"):
        Predictor(model).predict({"item_id": "TKT-1", "text": "Не могу войти в кабинет"})

def test_damaged_model(artifact, tmp_path):
    path = tmp_path / "broken.joblib"
    path.write_bytes(artifact.read_bytes() + b"broken")
    path.with_suffix(".json").write_bytes(artifact.with_suffix(".json").read_bytes())
    with pytest.raises(ModelUnavailableError):
        Predictor(ModelLoader(path)).predict({"item_id": "TKT-1", "text": "Не могу войти в кабинет"})

def test_unreadable_model(tmp_path):
    path = tmp_path / "invalid.joblib"
    path.write_bytes(b"this is not a joblib model")
    import sklearn
    meta = {"sklearn_version": sklearn.__version__, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    path.with_suffix(".json").write_text(json.dumps(meta))
    assert not ModelLoader(path).loaded

class BrokenModel:
    loaded = True
    version = "test"
    def predict(self, text):
        raise RuntimeError("Dependency failure")

def test_inference_failure():
    with pytest.raises(ModelUnavailableError, match="MODEL_INFERENCE_FAILED"):
        Predictor(BrokenModel()).predict({"item_id": "TKT-1", "text": "Не могу войти в кабинет"})

@pytest.mark.parametrize("category,confidence", [("WRONG", 0.9), ("ACCOUNT", float("nan")), ("ACCOUNT", 1.1)])
def test_invalid_model_output(category, confidence):
    class BadOutput(BrokenModel):
        def predict(self, text):
            return category, confidence
    with pytest.raises(ModelUnavailableError):
        Predictor(BadOutput()).predict({"item_id": "TKT-1", "text": "Не могу войти в кабинет"})

def test_normalization_is_identical(predictor):
    a = predictor.predict({"item_id": "TKT-1", "text": "не могу войти в учетную запись"})
    b = predictor.predict({"item_id": "TKT-2", "text": "  НЕ МОГУ   ВОЙТИ В УЧЁТНУЮ ЗАПИСЬ  "})
    assert a.prediction == b.prediction
    assert a.confidence == pytest.approx(b.confidence)

@pytest.mark.parametrize("category,confidence,expected", [
    ("ACCOUNT", 0.7999, ("OPERATOR", True)),
    ("ACCOUNT", 0.8, ("IT", False)),
    ("OTHER", 0.99, ("OPERATOR", True)),
])
def test_threshold_and_other(category, confidence, expected):
    assert choose_route(category, confidence) == expected
