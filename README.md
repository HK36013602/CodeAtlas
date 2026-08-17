# CodeAtlas

生产级代码架构分析平台。默认加载合成的 Java/Python 微服务仓库，也支持接入公开 GitHub/Gitee 仓库或上传 ZIP 源码，展示依赖图、循环依赖、复杂度、代码热点与风险诊断。

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

## 代码接入

在左侧选择“代码接入”：

- 公开仓库：输入 GitHub/Gitee HTTPS 地址，后台使用浅克隆分析。
- 本地项目：上传不超过 100 MB 的 ZIP 包。

当前真实扫描支持 Java 与 Python，识别模块、导入依赖、有效代码行、圈复杂度、连接度和热点文件。源码在任务结束后自动清理，分析摘要保存在 PostgreSQL。

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

默认示例标注为模拟数据；接入后的真实分析结果会标注“真实扫描”。
