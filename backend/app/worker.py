from celery import Celery
from app.config import get_settings
from app.services import refresh

settings = get_settings()
celery = Celery("codeatlas", broker=settings.redis_url, backend=settings.redis_url)

@celery.task(name="scan_repository")
def scan_repository() -> dict:
    return refresh()["summary"]
