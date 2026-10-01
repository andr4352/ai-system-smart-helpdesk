import json
from pydantic import ValidationError
from app.ml.errors import ModelUnavailableError
from app.ml.inference import ModelLoader
from app.services.prediction import Predictor

CASES = [
    {"item_id": "TKT-101", "text": "Не могу войти в свой личный кабинет"},
    {"item_id": "TKT-102", "text": "Подскажите когда будет пересдача экзамена"},
    {"item_id": "TKT-103", "text": "Моя оплата за обучение не отобразилась"},
    {"item_id": "TKT-104", "text": "Помогите пожалуйста разобраться"},
    {"item_id": "TKT-105", "text": ""},
]

def main():
    predictor = Predictor(ModelLoader())
    for request in CASES:
        print("Вход:", json.dumps(request, ensure_ascii=False))
        try:
            print(predictor.predict(request).model_dump_json(indent=2))
        except ValidationError as exc:
            print("INVALID_INPUT:", exc.errors(include_input=False, include_url=False))
        except ModelUnavailableError as exc:
            print("Ошибка модели:", str(exc))

if __name__ == "__main__":
    main()
