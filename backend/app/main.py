from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services import bootstrap
from app.worker import celery, scan_repository

@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap()
    yield

app = FastAPI(title="CodeAtlas API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5273"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
def health(): return {"status": "ok", "service": "CodeAtlas"}

@app.get("/api/v1/analysis")
def analysis(): return bootstrap()

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
