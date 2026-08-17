from celery import Celery
from app.config import get_settings
from pathlib import Path
import shutil
import subprocess
import zipfile
from app.analysis.repository import analyze_repository
from app.services import refresh, save_analysis

settings = get_settings()
celery = Celery("codeatlas", broker=settings.redis_url, backend=settings.redis_url)

@celery.task(name="scan_repository")
def scan_repository() -> dict:
    return refresh()["summary"]

@celery.task(name="scan_uploaded_repository")
def scan_uploaded_repository(job_id: str, source_type: str, source: str, name: str) -> dict:
    workspace = Path('/data/jobs') / job_id
    repo = workspace / 'repo'
    try:
        if source_type == 'git':
            subprocess.run(['git', 'clone', '--depth', '1', '--single-branch', source, str(repo)], check=True, timeout=180,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        else:
            repo.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(source) as archive:
                for member in archive.infolist():
                    target = (repo / member.filename).resolve()
                    if repo.resolve() not in target.parents and target != repo.resolve():
                        raise ValueError('ZIP 包含不安全路径。')
                archive.extractall(repo)
            children = [p for p in repo.iterdir() if p.is_dir()]
            if len(children) == 1 and not any(p.is_file() for p in repo.iterdir()): repo = children[0]
        payload = analyze_repository(repo, name)
        return {'analysis_id': save_analysis(payload), 'repository': payload['repository'], 'summary': payload['summary']}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
