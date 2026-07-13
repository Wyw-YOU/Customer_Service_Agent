# AI Digital Mall Customer Service Agent

基于 LangGraph + RAG + Tool Calling 的电商客服 Agent MVP。

## 核心能力

- **Multi-step Agent Workflow** — LangGraph 驱动的多步骤 Agent 编排
- **Product / Order / Refund Tools** — Agent 调用业务系统工具
- **RAG Knowledge Retrieval** — 向量检索 + 混合搜索知识增强
- **Human-in-the-loop Approval** — 敏感操作人工审批流程
- **Agent Trace** — 全链路执行追踪与调试
- **Offline Evaluation** — 离线评估脚本和报告
- **Docker Compose Target** — Compose 路径已修正并通过配置校验，完整容器启动仍待实机验证

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Agent Runtime | LangGraph |
| LLM | OpenAI Compatible API (DeepSeek / Qwen) |
| RAG | Qdrant + Embedding + Hybrid Search |
| Backend | FastAPI + SQLAlchemy + Pydantic |
| Frontend | Next.js + React + CSS |
| Database | PostgreSQL + Redis |
| Deployment | Docker Compose + Nginx |

## 快速开始

### 环境要求

- Docker & Docker Compose v2+
- Python 3.12+
- Node.js 20 LTS

### 后端本地启动

```bash
git clone <repo-url>
cd Customer_Service_Agent/backend

copy .env.example .env
# 编辑 backend/.env 填写数据库、Qdrant、Redis、LLM、JWT 配置

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

- API Health：`http://localhost:8000/health`
- Swagger：`http://localhost:8000/docs`

### Docker Compose 状态

`deployment/docker-compose.yml` 已按当前仓库结构修正路径：

- backend build context：`../backend`
- backend env file：`../backend/.env`
- frontend build context：`../frontend`
- nginx build context：`./nginx`

已通过 `docker compose -f deployment\docker-compose.yml config --quiet` 配置校验。完整 `docker compose up -d`、镜像构建和服务健康检查仍需在目标机器上执行后才能标记为一键启动通过。详见 `deployment/README.md`。

### 前端页面

```bash
cd Customer_Service_Agent/frontend
npm.cmd install
npm.cmd run dev
```

访问：

- Login：`http://localhost:3000/login`
- Chat：`http://localhost:3000/chat`
- Trace：`http://localhost:3000/admin/traces`
- Approval：`http://localhost:3000/admin/approvals`

默认 API 地址为 `http://localhost:8000`，可通过 `NEXT_PUBLIC_API_BASE_URL` 覆盖。登录后左侧工作区导航可在 Chat、Trace、Approval 之间切换，侧栏支持折叠，右上角显示当前账号头像、用户 id 和角色。

## 项目结构

```
AI-Digital-Mall-Agent/
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── domains/
│       ├── agent/
│       ├── rag/
│       ├── tools/
│       └── services/
├── frontend/
├── evaluation/
│   ├── datasets/
│   ├── metrics/
│   └── runner.py
├── deployment/
├── tests/
└── docs/
```

## MVP 功能范围

### 用户端
- AI 聊天入口
- 商品咨询与基础推荐
- 订单查询
- 售后申请入口
- RAG 引用展示

### Agent 能力
- LangGraph Workflow + Intent Router
- Tool Calling (Product / Order / Refund)
- RAG Retrieval + Safety Guard
- Human-in-the-loop 审批任务
- Agent Trace

### 管理端
- Agent Trace 查看
- Refund Approval 审批页面

## 评估指标

| 指标 | MVP 目标 |
| --- | --- |
| Intent Accuracy | >= 90% |
| Tool Selection Accuracy | >= 90% |
| Tool Parameter Accuracy | >= 90% |
| Safety Compliance | 100% |
| Retrieval Recall@5 | >= 80% |

## License

MIT
