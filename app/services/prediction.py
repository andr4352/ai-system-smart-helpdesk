ROUTES = {"ACCOUNT": "IT", "STUDY": "DEAN_OFFICE",
          "PAYMENT": "FINANCE", "OTHER": "OPERATOR"}

def choose_route(category: str, confidence: float):
    manual = confidence < 0.8 or category == "OTHER"
    return ("OPERATOR" if manual else ROUTES[category]), manual
