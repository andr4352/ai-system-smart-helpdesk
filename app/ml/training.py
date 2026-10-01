import csv
import hashlib
import json
import platform
from pathlib import Path
import joblib
import numpy
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from app.ml.preprocessing import normalize
from app.schemas import PredictionRequest

ROOT = Path(__file__).resolve().parents[2]
VERSION = "helpdesk-tfidf-lr-1.0.0"
CLASSES = {"ACCOUNT", "STUDY", "PAYMENT", "OTHER"}

def train(data_path=ROOT / "data/demo_train.csv", output_dir=ROOT / "artifacts"):
    data_path, output_dir = Path(data_path), Path(output_dir)
    with data_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    texts, labels = [], []
    for row in rows:
        request = PredictionRequest(item_id=row["item_id"], text=row["text"])
        if row["label"] not in CLASSES:
            raise ValueError("Неизвестная метка")
        texts.append(request.text)
        labels.append(row["label"])
    if set(labels) != CLASSES or len(set(map(normalize, texts))) != len(texts):
        raise ValueError("Нужны четыре класса и тексты без дублей")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2))),
        ("classifier", LogisticRegression(C=10, max_iter=1000, random_state=42)),
    ])
    pipeline.fit(texts, labels)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "helpdesk.joblib"
    joblib.dump(pipeline, model_path)
    metadata = {
        "model_version": VERSION, "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(), "numpy_version": numpy.__version__,
        "scipy_version": scipy.__version__, "joblib_version": joblib.__version__,
        "classes": sorted(CLASSES), "samples": len(rows), "threshold": 0.8,
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
    }
    model_path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return model_path

if __name__ == "__main__":
    print(train())
