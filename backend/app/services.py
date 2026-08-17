from sqlalchemy import text
from app.analysis.engine import build_snapshot
from app.db import SessionLocal

def bootstrap() -> dict:
    with SessionLocal.begin() as session:
        # Uvicorn may start multiple workers at once. The transaction-scoped
        # advisory lock keeps the initial snapshot idempotent across processes.
        session.execute(text("SELECT pg_advisory_xact_lock(hashtext('codeatlas:bootstrap'))"))
        row = session.execute(text("SELECT payload FROM analyses ORDER BY created_at DESC LIMIT 1")).scalar_one_or_none()
        if row:
            return row
        payload = build_snapshot()
        session.execute(text("INSERT INTO analyses(repository_name, commit_sha, payload) VALUES (:name,:sha,CAST(:payload AS jsonb))"),
                        {"name": payload["repository"]["name"], "sha": payload["repository"]["commit"], "payload": __import__('json').dumps(payload, ensure_ascii=False)})
        return payload

def refresh() -> dict:
    payload = build_snapshot()
    with SessionLocal.begin() as session:
        session.execute(text("INSERT INTO analyses(repository_name, commit_sha, payload) VALUES (:name,:sha,CAST(:payload AS jsonb))"),
                        {"name": payload["repository"]["name"], "sha": payload["repository"]["commit"], "payload": __import__('json').dumps(payload, ensure_ascii=False)})
    return payload

def save_analysis(payload: dict) -> int:
    with SessionLocal.begin() as session:
        return session.execute(text("INSERT INTO analyses(repository_name, commit_sha, payload) VALUES (:name,:sha,CAST(:payload AS jsonb)) RETURNING id"),
            {"name": payload["repository"]["name"], "sha": payload["repository"]["commit"], "payload": __import__('json').dumps(payload, ensure_ascii=False)}).scalar_one()

def get_analysis(analysis_id: int | None = None) -> dict:
    with SessionLocal() as session:
        if analysis_id is None:
            row = session.execute(text("SELECT payload FROM analyses ORDER BY created_at DESC LIMIT 1")).scalar_one_or_none()
        else:
            row = session.execute(text("SELECT payload FROM analyses WHERE id=:id"), {"id": analysis_id}).scalar_one_or_none()
        if row is None:
            raise LookupError('分析结果不存在。')
        return row
