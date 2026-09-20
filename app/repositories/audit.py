from pathlib import Path
import sqlite3

class AuditRepository:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS predictions "
                       "(request_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")

    def ready(self):
        try:
            with sqlite3.connect(self.path, timeout=1) as db:
                db.execute("SELECT request_id FROM predictions LIMIT 1")
            return True
        except sqlite3.Error:
            return False

    def save(self, result):
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO predictions VALUES (?, ?)",
                       (str(result.request_id), result.model_dump_json()))
