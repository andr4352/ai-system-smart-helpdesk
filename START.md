# Локальный запуск ЛР3

Python 3.12. Команды выполняются из корня проекта, в ветке feature/lab3-component.

```bash
git clone --branch feature/lab3-component https://github.com/andr4352/ai-system-smart-helpdesk.git
cd ai-system-smart-helpdesk
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux и macOS:

```bash
source .venv/bin/activate
```

Затем на любой системе:

```bash
python -m pip install -r requirements-component.txt
python -m app.ml.training
python -m app.demo
python -m pytest tests/test_component.py -q
```

Обучение создаёт artifacts/helpdesk.joblib и artifacts/helpdesk.json из data/demo_train.csv. Используйте именно этот собственный артефакт. При обновлении библиотек пересоздайте его. Чужие joblib не загружайте: SHA-256 обнаруживает повреждение, но не подтверждает безопасность файла.

Демонстрация запускается без сервера, сети и API-ключей. Вывод включает разные категории, передачу человеку и ошибку пустого ввода. UUID меняется при каждом запуске. Если артефакта нет, выводится MODEL_NOT_READY; выполните обучение.

## Необязательная проверка прежнего API

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Для запуска API задайте API_KEY локально. PowerShell: `$env:API_KEY="ваш-локальный-ключ"`; Linux/macOS: `export API_KEY="ваш-локальный-ключ"`.

```bash
python -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs. Нужен заголовок X-API-Key. По умолчанию модель берётся из artifacts/helpdesk.joblib; иной путь задаётся MODEL_PATH. При отсутствии или повреждении модели /health и /predict возвращают 503. Базовый Docker-образ по-прежнему не содержит весов: передайте свой каталог artifacts как том /service/artifacts.
