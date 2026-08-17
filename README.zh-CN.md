# CodeAtlas

[English](README.md)

CodeAtlas 是一个生产级代码架构分析平台。它可以分析公开 GitHub/Gitee 仓库或用户上传的源码压缩包，并展示模块依赖、循环依赖、复杂度、代码热点和架构风险。项目还内置一个合成的 Java/Python 微服务仓库，启动后即可体验。

## 核心能力

- 通过浅克隆接入公开 GitHub 和 Gitee 仓库
- 上传最大 100 MB 的本地 ZIP 源码包
- 解析 Java 与 Python 模块和导入关系
- 计算有效代码行、圈复杂度、连接度和热点评分
- 可视化依赖拓扑和循环依赖
- 将代码接入、架构地图、风险诊断和文件分析拆分为独立路由工作台
- 使用 Celery 异步处理仓库
- 分析完成后自动清理临时源码
- 将分析摘要持久化到 PostgreSQL

## 技术架构

- **前端：** Vue 3、TypeScript、ECharts、Nginx
- **API 与任务：** FastAPI、Celery
- **数据存储：** PostgreSQL
- **队列与缓存：** Redis
- **运行环境：** Docker Compose

## 快速启动

确保 Docker Desktop 已启动，然后在项目根目录执行：

```powershell
docker compose up --build -d
docker compose ps
```

- 分析工作台：http://localhost:5273
- API 文档：http://localhost:8100/docs

## 分析代码仓库

在左侧导航进入“代码接入”，然后选择一种方式：

- **公开仓库：** 输入公开 GitHub 或 Gitee HTTPS 地址，后台会先执行浅克隆再开始分析。
- **本地项目：** 上传不超过 100 MB 的 ZIP 源码包。

当前真实扫描支持 Java 与 Python，可识别模块、导入依赖、有效代码行、圈复杂度、连接度和热点文件。源码会在任务结束后自动清理，仅将分析摘要保存在 PostgreSQL。

## 测试

```powershell
cd backend
$env:PYTHONPATH='.'
python -m pytest tests -q
```

## 停止服务

```powershell
docker compose down
```

内置示例会明确标注为模拟数据；接入仓库后生成的结果会标注为真实扫描。
