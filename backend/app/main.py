from contextlib import asynccontextmanager
from pathlib import Path
import re
from urllib.parse import urlparse
from uuid import uuid4
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.services import bootstrap, get_analysis
from app.worker import celery, scan_repository, scan_uploaded_repository

@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap()
    yield

app = FastAPI(title="CodeAtlas API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5273"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
def health(): return {"status": "ok", "service": "CodeAtlas"}

@app.get("/api/v1/analysis")
def analysis(analysis_id: int | None = None):
    try: return get_analysis(analysis_id) if analysis_id else bootstrap()
    except LookupError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post("/api/v1/scans", status_code=202)
def create_scan():
    try:
        task = scan_repository.delay()
        return {"task_id": task.id, "status": "queued"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="扫描队列暂不可用，请稍后重试。") from exc

@app.get("/api/v1/scans/{task_id}")
def scan_status(task_id: str):
    task = celery.AsyncResult(task_id)
    payload = {"task_id": task_id, "status": task.status.lower()}
    if task.successful():
        payload["result"] = task.result
    elif task.failed():
        payload["error"] = "扫描任务执行失败。"
    return payload

def _valid_repo_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == 'https' and parsed.hostname in {'github.com', 'www.github.com', 'gitee.com', 'www.gitee.com'} and bool(re.fullmatch(r'/[\w.-]+/[\w.-]+(?:\.git)?/?', parsed.path))

@app.post('/api/v1/repositories/git', status_code=202)
def scan_git(repository_url: str = Form(...)):
    url = repository_url.strip()
    if not _valid_repo_url(url):
        raise HTTPException(status_code=400, detail='仅支持 GitHub 或 Gitee 的公开 HTTPS 仓库地址。')
    job_id = uuid4().hex
    name = Path(urlparse(url).path.rstrip('/')).stem
    task = scan_uploaded_repository.delay(job_id, 'git', url, name)
    return {'task_id': task.id, 'status': 'queued', 'repository_name': name}

@app.post('/api/v1/repositories/upload', status_code=202)
async def scan_zip(file: UploadFile = File(...)):
    filename = Path(file.filename or '').name
    if not filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail='请上传 ZIP 格式的项目源码。')
    job_id = uuid4().hex
    workspace = Path('/data/jobs') / job_id
    workspace.mkdir(parents=True, exist_ok=False)
    target = workspace / 'source.zip'
    size = 0
    try:
        with target.open('wb') as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > 100 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail='ZIP 不能超过 100 MB。')
                output.write(chunk)
        task = scan_uploaded_repository.delay(job_id, 'zip', str(target), Path(filename).stem)
        return {'task_id': task.id, 'status': 'queued', 'repository_name': Path(filename).stem}
    except Exception:
        if target.exists(): target.unlink()
        if workspace.exists(): workspace.rmdir()
        raise
