# CodeAtlas

[简体中文](README.zh-CN.md)

CodeAtlas is a production-oriented software architecture analysis platform. It can analyze public GitHub or Gitee repositories and uploaded source archives, then visualize module dependencies, cycles, complexity, code hotspots, and architectural risks. A synthetic Java/Python microservice repository is included for immediate exploration.

## Highlights

- Ingest public GitHub and Gitee repositories through shallow cloning
- Upload local source code as a ZIP archive up to 100 MB
- Parse Java and Python modules and imports
- Measure effective lines of code, cyclomatic complexity, connectivity, and hotspot scores
- Visualize dependency topology and circular dependencies
- Separate repository ingestion, architecture map, risk, and file analysis into routed workspaces
- Process repositories asynchronously with Celery
- Remove temporary source files when analysis completes
- Persist analysis summaries in PostgreSQL

## Architecture

- **Frontend:** Vue 3, TypeScript, ECharts, Nginx
- **API and workers:** FastAPI, Celery
- **Storage:** PostgreSQL
- **Queue and cache:** Redis
- **Runtime:** Docker Compose

## Quick start

Make sure Docker Desktop is running, then execute from the repository root:

```powershell
docker compose up --build -d
docker compose ps
```

- Analysis workspace: http://localhost:5273
- OpenAPI documentation: http://localhost:8100/docs

## Analyze a repository

Open **Repository ingestion** in the left navigation and choose either:

- **Public repository:** enter a public GitHub or Gitee HTTPS URL. The worker performs a shallow clone before analysis.
- **Local project:** upload a ZIP archive no larger than 100 MB.

The current scanner supports Java and Python. It extracts modules, import dependencies, effective lines of code, cyclomatic complexity, connectivity, and hotspot files. Temporary source files are deleted after processing; only the analysis summary is retained in PostgreSQL.

## Tests

```powershell
cd backend
$env:PYTHONPATH='.'
python -m pytest tests -q
```

## Stop the stack

```powershell
docker compose down
```

The bundled example is explicitly labeled as synthetic data. Results created from an ingested repository are labeled as a real scan.
