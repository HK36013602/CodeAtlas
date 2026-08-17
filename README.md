# CodeAtlas

生产级代码架构分析演示平台。默认加载合成的 Java/Python 微服务仓库，展示依赖图、循环依赖、复杂度、代码热点、变更耦合与风险诊断。

## 技术栈

- Vue 3、TypeScript、ECharts、Nginx
- FastAPI、Celery
- PostgreSQL、Redis
- Docker Compose

## 启动

```powershell
cd C:\Users\ASUS\Desktop\CodeAtlas
docker-compose up --build -d
```

- 工作台：http://localhost:5273
- API 文档：http://localhost:8100/docs

## 测试

```powershell
cd backend
$env:PYTHONPATH='.'
python -m pytest tests -q
```

## 停止

```powershell
docker-compose down
```

默认数据为模拟数据。真实仓库接入时可在 `backend/app/analysis` 下扩展 Git 克隆、AST/Tree-sitter 解析与提交历史适配器，现有 API 和界面数据契约无需改变。
