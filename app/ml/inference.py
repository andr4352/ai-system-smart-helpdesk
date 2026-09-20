class ModelLoader:
    """Интерфейс загрузчика. Обучение и загрузка — следующие ЛР."""
    loaded = False
    version = None

    def predict(self, text: str):
        raise RuntimeError("MODEL_NOT_READY")
