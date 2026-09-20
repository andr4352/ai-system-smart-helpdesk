# Запуск каркаса

Python 3.12. Команды выполняются из каталога проекта.

```bash
python -m venv .venv
# Windows PowerShell: .venv/Scripts/Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
# PowerShell: $env:API_KEY="ваш-локальный-ключ"
# Linux/macOS: export API_KEY="ваш-локальный-ключ"
python -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs. Для каждого метода передать X-API-Key.
Модель намеренно не обучена: /health и корректный /predict отвечают 503,
/metrics отвечает 200. Это каркас ЛР 2, а не готовый классификатор.
Проверки используют временную подмену модели, не оценивают качество ML.
Плановые SLA, ограничения прокси и контур обучения описаны в README.

## Репозиторий

https://github.com/andr4352/ai-system-smart-helpdesk

Для загрузки проекта:

```bash
git clone https://github.com/andr4352/ai-system-smart-helpdesk.git
cd ai-system-smart-helpdesk
```
