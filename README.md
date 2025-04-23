# 🤖 Agents Orchestration System using LangGraph & MCP

This project is a multi-agent orchestration system designed to simulate an underwriting pipeline, where each agent performs a specific task (document verification, screening, eligibility checking, report generation). Built on top of **LangGraph**, it uses the **Model Context Protocol (MCP)** for tool calls, chat orchestration, and graph-based state management.

---

## 📦 Project Structure

Each agent is a modular component with its own:
- Kafka event listeners
- FastAPI controller
- LangGraph-compatible remote interface
- MCP

The **Bank Office Agent** coordinates all others using a graph-based workflow.

---

## 🛠 Setup Instructions

### 🔀 1. Clone and Setup Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🔐 2. Create `.env` File
```env
# .env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1

LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=http://localhost:3000

POSTGRES_CONN_STRING=postgresql://postgres:123456@localhost:5433/MCP-Agent
SSE_SERVER_URL=http://127.0.0.1:9090/sse
```

---

## 🚀 Run Individual Agents

Each agent requires three processes:
1. LangGraph-compatible backend (`server.py`)
2. Kafka event listener
3. FastAPI controller (exposes it as a `RemoteGraph` node)

### 🏦 Bank Office Agent (Run every commands in a separate terminal)
```bash
python server.py
python3 -m Bank_Office_Agent.kafka.listener
uvicorn Bank_Office_Agent.controllers.main:bankagent --reload
```

### 📄 Document Verification Agent (Run every commands in a separate terminal)
```bash
python server.py
python3 -m Document_Verification_Agent.kafka.listener
uvicorn Document_Verification_Agent.controllers.main:documentagent --reload
```

### 🔍 Screening Ops Maker Agent (Run every commands in a separate terminal)
```bash
python server.py
python3 -m Screening_Ops_Maker_Agent.kafka.listener
uvicorn Screening_Ops_Maker_Agent.controllers.main:screeningagent --reload
```

### ✅ Eligibility Checker Agent (Run every commands in a separate terminal)
```bash
python server.py
python3 -m Eligibility_Check_Agent.kafka.listener
uvicorn Eligibility_Check_Agent.controllers.main:eligibilityagent --reload
```

### 📝 Report Generation Agent (Run every commands in a separate terminal)
```bash
python server.py
python3 -m Report_Generation_Agent.kafka.listener
uvicorn Report_Generation_Agent.controllers.main:reportagent --reload
```

---

## 🧠 Run the Full Application (Graph Execution) 
```bash
# Activate environment if not already
source venv/bin/activate
python server.py in a separate terminal

# Run main app
fastapi dev   # or use
uvicorn main:app --reload
```

---

## 🔍 Features

- ✅ Fully async architecture with LangGraph's `RemoteGraph` nodes
- 🧠 Natural language reasoning with LLM tool calling
- 💾 Kafka-driven tool orchestration
- 🔎 Modular agent setup with well-defined responsibilities
- 📊 Langfuse integration for observability and tracing

---

## 🧺 Tech Stack

| Tool       | Purpose                        |
|------------|--------------------------------|
| LangGraph  | Agent coordination as a DAG    |
| MCP        | Structured tool calling        |
| Ollama     | Local LLM inference            |
| Kafka      | Event-based message handling   |
| FastAPI    | RESTful interface per agent    |
| PostgreSQL | Graph checkpointing            |
| Langfuse   | Monitoring and trace logs      |

---


