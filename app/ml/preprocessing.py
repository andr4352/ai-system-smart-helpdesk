def normalize(text: str) -> str:
    """Общая нормализация для будущего Pipeline обучения и сервиса."""
    return " ".join(text.lower().replace("ё", "е").split())
