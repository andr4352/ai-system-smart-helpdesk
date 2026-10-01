def normalize(text: str) -> str:
    """Одна нормализация для обучения и обработки новых обращений."""
    return " ".join(text.lower().replace("ё", "е").split())
