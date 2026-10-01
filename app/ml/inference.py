import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import sklearn
from sklearn.pipeline import Pipeline
from app.ml.errors import ModelUnavailableError

DEFAULT_MODEL = Path(__file__).resolve().parents[2] / "artifacts/helpdesk.joblib"

class ModelLoader:
    """Загружает только собственный артефакт, созданный командой training."""
    def __init__(self, model_path=DEFAULT_MODEL):
        self.loaded = False
        self.version = None
        self.pipeline = None
        self.error = "MODEL_NOT_READY"
        try:
            path = Path(model_path)
            meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
            if meta["sklearn_version"] != sklearn.__version__:
                raise ValueError("Версия scikit-learn отличается")
            if hashlib.sha256(path.read_bytes()).hexdigest() != meta["sha256"]:
                raise ValueError("Контрольная сумма не совпадает")
            # SHA-256 проверяет целостность, но не делает чужой joblib безопасным.
            pipeline = joblib.load(path)
            if not isinstance(pipeline, Pipeline):
                raise ValueError("Ожидался Pipeline")
            if set(pipeline.classes_) != {"ACCOUNT", "STUDY", "PAYMENT", "OTHER"}:
                raise ValueError("Неверные классы модели")
            if not isinstance(meta["model_version"], str) or not meta["model_version"]:
                raise ValueError("Нет версии модели")
            self.pipeline, self.version = pipeline, meta["model_version"]
            self.loaded = True
        except Exception:
            self.error = "MODEL_NOT_READY"

    def predict(self, text: str) -> tuple[str, float]:
        if not self.loaded:
            raise ModelUnavailableError(self.error)
        try:
            probabilities = self.pipeline.predict_proba([text])[0]
            if (len(probabilities) != 4 or not np.isfinite(probabilities).all()
                    or (probabilities < 0).any() or (probabilities > 1).any()
                    or not np.isclose(probabilities.sum(), 1.0)):
                raise ValueError("Неверные оценки модели")
            index = int(probabilities.argmax())
            return str(self.pipeline.classes_[index]), float(probabilities[index])
        except Exception as exc:
            raise ModelUnavailableError("MODEL_INFERENCE_FAILED") from exc
