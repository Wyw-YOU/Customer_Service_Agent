# AI Digital Mall Customer Service Agent

基于 LangGraph + RAG + Tool Calling 的电商客服 Agent MVP。

## 核心能力

- **Multi-step Agent Workflow** — LangGraph 驱动的多步骤 Agent 编排
- **Product / Order / Refund Tools** — Agent 调用业务系统工具
- **RAG Knowledge Retrieval** — 向量检索 + 混合搜索知识增强
- **Human-in-the-loop Approval** — 敏感操作人工审批流程
- **Agent Trace** — 全链路执行追踪与调试
- **Offline Evaluation** — 离线评估脚本和报告
- **Docker Compose Quick Start** — 一键启动完整环境

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Agent Runtime | LangGraph |
| LLM | OpenAI Compatible API (DeepSeek / Qwen) |
| RAG | Qdrant + Embedding + Hybrid Search |
| Backend | FastAPI + SQLAlchemy + Pydantic |
| Frontend | Next.js + React + Tailwind CSS |
| Database | PostgreSQL + Redis |
| Deployment | Docker Compose + Nginx |

## 快速开始

### 环境要求

- Docker & Docker Compose v2+
- Python 3.12+
- Node.js 20 LTS

### 启动

```bash
git clone <repo-url>
cd AI-Digital-Mall-Agent

cp .env.example .env
# 编辑 .env 填写 LLM API Key

docker compose up -d
```

访问 `http://localhost`

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
