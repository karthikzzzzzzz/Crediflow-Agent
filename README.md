
# Crediflow-agent

Crediflow-agent is an advanced AI-driven automation platform designed to overhaul and streamline the manual processes. By leveraging agentic AI — which integrates business logic, contextual history, and large language models (LLMs) — Crediflow-agent continuously observes, reasons, and takes action across complex workflows, enabling end-to-end intelligent automation.

## Features

- **Modular Monolith Multi-Agent Architecture**: The system is composed of several agents, each encapsulated in its own module, facilitating maintainability and scalability.​ The project implements a modular monolith architecture using FastAPI and Dependency Injector, enabling clean separation of concerns across specialized agents like Document Verification, Eligibility Check, and Data Acquisition, etc.. Each agent is structured as an independent FastAPI module with loosely coupled services managed via Dependency Injector, ensuring singleton instances and testable, maintainable code.
- **LangGraph Integration**: Utilizes LangGraph to define and manage the workflow graph, enabling clear visualization and control over the process flow.
- **MCP Compatibility**: Employs Model Context Protocol to standardize interactions between agents and external tools or servers, promoting interoperability. The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools.
- **Self-Hosted Observability with Langfuse**: All agent activities, traces, spans, and metadata are logged and visualized using a self-hosted Langfuse instance. This provides deep visibility into agent behavior, performance, and decision-making, supporting observability, debugging, and lineage tracking across workflows.
- **Memory Management with LangMem**: Agents use LangMem to manage and persist contextual memory across steps and sessions, enabling coherent, context-aware decision-making throughout long-running workflows.
- **Event-Driven System with Kafka Listeners**: The system follows an event-driven architecture where each agent consumes events from its dedicated Kafka topic. This decouples processing logic, ensures scalability, and enables asynchronous execution of agent workflows
- **StateGraph Memory Management with Redis & PostgreSQL**: For managing agent state across workflow executions, the system uses Redis for fast, short-term in-memory state during active graph runs, and PostgreSQL for persistent, long-term state storage and recovery. This hybrid setup ensures responsive execution and reliable state retention.
- **Real-Time Communication with SSE**: Uses Server-Sent Events (SSE) to stream real-time updates from the server to the client, enabling users to receive live feedback on agent progress, statuses, and decision points.
- **Dockerized for Deployment**: The entire platform is containerized with Docker, making it easy to deploy, scale, and manage across different environments
- **LangChain-MCP Adapters Integration**: The project integrates with langchain-mcp-adapters to standardize agent orchestration and communication across MCP (Model Context Protocol) ecosystem, enabling seamless plug-and-play with existing LangGraph agents and tools

## Technology Used
Crediflow-agent uses a number of open source projects as shown below:-

| Framework | Description |
| --------- | ----------- |
| LangGraph | A framework for building stateful, multi-step AI workflows using a graph-based structure; used here to orchestrate agentic decision flows. |
| LangFuse  | An observability and tracing platform for LLM applications; self-hosted in this project to monitor spans, traces, and metadata across agent workflows. |
| LangMem   | A memory management library for LLMs; used to persist and retrieve contextual information across sessions, enhancing coherence in agent interactions. |
| FastAPI   | A modern, high-performance Python web framework used for building each modular agent’s API with dependency injection and asynchronous capabilities. |
| Model Context Protocol  | The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. |


## Tech Stack Summary

| Framework     | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| LangGraph     | Framework to build stateful, agentic workflows using graph structures.      |
| LangFuse      | Observability and monitoring platform for LLM applications.                 |
| LangMem       | Lightweight memory module to manage state across agent interactions.        |
| FastAPI       | Web framework for building APIs quickly with automatic docs support.         |
| Redis         | In-memory store for short-term memory and transient states.                 |
| PostgreSQL    | Long-term memory/state storage for agent decisions and logs.                |
| Kafka         | Event streaming platform for agent communication and event-driven flow.     |
| SSE (Server-Sent Events) | Real-time server-to-client communication channel.               |
| Dependency Injector | For modular service wiring and singleton instance management.         |
| Docker        | Containerization for local development and deployment.                      |
| LangChain MCP Adapters | Extensions to plug LangChain agents into LangGraph workflows.      |


## Project Structure
```
Crediflow-agent/
├── Back_office_agent/                # Agent for handling post-processing and admin tasks  
├── Data_acquisition_agent/           # Gathers data from various sources
│   ├── controllers/                  # FastAPI route handlers
│   ├── dependencies/                 # Dependency Injector containers and wiring
│   ├── kafka/                        # Kafka listener to consume messages
│   └── services/                     # Business logic layer
├── Document_verification_agent/      # Validates submitted documents
├── Eligibility_check_agent/          # Checks applicant eligibility
├── Human_in_the_loop/                # Supports human intervention in workflows
├── Report_generation_agent/          # Compiles decisions and outputs reports
├── Screening_ops_maker_agent/        # Coordinates screening operations
├── utils/                            # Shared utilities and core modules
│   ├── database.py                   # Database session and connection setup
│   ├── models.py                     # SQLAlchemy ORM models
│   └── schemas.py                    # Pydantic data validation schemas
├── .gitignore                        # Git ignore rules
├── Docker-compose.yaml               # Docker Compose config for multi-service orchestration
├── Dockerfile                        # Dockerfile for building main agent image
├── Dockerfile.server                 # Dockerfile for server-specific deployment
├── langgraph.json                    # LangGraph configuration                     
├── main.py                           # Application Entry Point
├── server.py                         # MCP Server
├── supervisord.conf                  # Supervisor config for managing multiple processes
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```


## Installation

```sh
cd Crediflow-agent
python -m venv <virtual-env-name>
source <virtual-env-name>/bin/activate  # For Linux/macOS
# Or use: .\<virtual-env-name>\Scripts\activate  # For Windows
```

## Development

How to setup Local Development Environment and get started

## Setup Instructions

### 1. Open the Folder & Create a Virtual Environment

```bash
cd Crediflow-agent
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
brew install services kafka zookeeper 
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest

```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following content:

```env
# .env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1

LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=<your-self-hosted-localhost>
SSE_SERVER_URL=<your-sse-localhost>

KAFKA_BOOTSTRAP_SERVERS=<kakfa-9092>

KAFKA_GROUP=<group-name>
MODEL=<ollama-model>

POSTGRES_CONN_STRING=<your-db-connection>

REDIS_URI=<your-redis-url>
```

---

## Running Individual Agents

    Each agent consists of three components to be run in separate terminals:
    1. LangGraph-compatible backend (`server.py`)
    2. Kafka event listener
    3. FastAPI controller exposing the agent as a 

> Run each block below in separate terminal sessions.

### Start the server in a terminal
- Python server.py

### Back Office Agent
```bash
python3 -m Back_office_agent.kafka.listener
uvicorn Back_office_agent.controllers.main:bankagent --reload
```

### Data Acquisition Agent
```bash
python3 -m Data_acquistion_agent.kafka.listener
uvicorn Data_acquistion_agent.controllers.main:dataagent --reload
```

### Document Verification Agent
```bash
python3 -m Document_verification_agent.kafka.listener
uvicorn Document_verification_agent.controllers.main:documentagent --reload
```

### Screening Ops Maker Agent
```bash
python3 -m Screening_ops_maker_agent.kafka.listener
uvicorn Screening_ops_maker_agent.controllers.main:screeningagent --reload
```

### Eligibility Checker Agent
```bash
python3 -m Eligibility_check_agent.kafka.listener
uvicorn Eligibility_check_agent.controllers.main:eligibilityagent --reload
```

### Report Generation Agent
```bash
python3 -m Report_generation_agent.kafka.listener
uvicorn Report_generation_agent.controllers.main:reportagent --reload
```

---

## Running the Full Application

```bash
# Start backend
python server.py

# Start main FastAPI app in another terminal
uvicorn main:app --reload
# Or
fastapi dev
```
### Access the Application

Visit in your browser:
```
http://127.0.0.1:8000
```

---

## Docker

### Build and Start Using Docker Compose

```bash
cd Crediflow-agent
docker-compose up -d --build
```

### Access the Application

Visit in your browser:
```
http://127.0.0.1:8000
```

---
For production release:

```sh
# Build and start containers in detached mode
docker-compose up -d --build

#You can stop the container
docker-compose down
```

### Curl Commands

```bash
curl -X POST http://localhost:8000/Crediflow-agent/<agent-name>/v1/realms/{realmID}/users/{userID}/leads/{leadID}/session/{session_id}/decision \
     -H "Content-Type: application/json" \
     -d '{
           "text": ""
         }'
```

### Debugging
All observations, traces, and explainability metadata across agents are tracked and visualized using a self-hosted Langfuse instance.

### Follow the steps in this docs to setup

- https://langfuse.com/self-hosting

## Memory Management
This system implements a hybrid memory architecture to balance responsiveness, traceability, and explainability for AI agents. It distinguishes between short-term (working) memory and various forms of long-term memory, inspired by cognitive science


| Framework | Type | Database |TTL |
| ------ | ------ |------ |------ |
| ShortTerm |  State Graph| Redis |60 min
| LongTerm | Explainability | PostgreSQL| n/a
| LongTerm | Procedural | Redis| 60 min
| ShortTerm  | ChatHistory | Redis|  60 min
| LongTerm | ChatHistory | PostgreSQL|  n/a
| LongTerm | Semantic | PostgreSQL (PgVect)| n/a
| LongTerm | Episodic | PostgreSQL | n/a
| LongTerm | Episodic (Past Transaction) | PostgreSQL | n/a
| LongTerm | Checkpoints | AWS S3 | n/a

> **_NOTE-1:_**  Chat History should be stored in Short term memory (HOT Store) and Long term memory (Cold Store).

> **_NOTE-2:_**  Custom columns like userID, realmID, leadID should be stored as additional metadata

### Short-Term Memory (HOT Store)

**Tech Used**: Redis  
**Purpose**: Short-term memory is used to **store intermediate or recent context/stategraph** from a user-agent interaction. It supports fast reads/writes and is ideal for use during multi-turn conversations or in-session tool usage.

**Key Features**:
- Cached per `session_id`
- Automatically expires (TTL = 10 minutes by default)
- Lightweight JSON structure

**Implementation**:
- Serialized agent state is stored in Redis via `persist_state_to_shortterm`.
- TTL ensures that memory is cleared after a period of inactivity.
- Useful for rapid checkpoint recovery during LangGraph workflows.

```python
self.persist_state_to_shortterm(session_id, state, ttl=600)
```

---

### Long-Term Memory (COLD Store)

**Tech Used**: PostgreSQL  
**Purpose**: Long-term memory is designed to persist critical knowledge, events, and stategraph data that may span across sessions. This includes factual knowledge (semantic memory), past experiences (episodic memory), and procedural workflows (procedural memory). It ensures that the agent:

- Retains important information even after short-term memory expires
- Can recover from crashes by reconstructing its state using previously stored memory
- Remains explainable and consistent over time
- This memory is typically stored in PostgreSQL and AWS S3, depending on the type.

**Stored in Tables**:
- `intelli_agent` (Session state archive)
- `episodic_memory`
- `semantic_memory`
- `agent_procedural_memory`

**Metadata Included**:
- `user_id`, `realm_id`, `lead_id`
- `trace_id`, `span_id`
- `session_id`, `case_id`
- `timestamp`, `tags`, `vector`, etc.


```python
self.persist_state_to_longterm(session_id, user_id, realm_id, lead_id, trace_id, span_id, state)
```

---

### Episodic Memory

**Purpose**:  Captures **user-agent interaction summaries** and raw state snapshots that occurred during a specific point in time.

**Think of it as**: The "journal entries" or "stories" the agent remembers from past experiences.

**Use Cases**:
- Replayability and agent transparency
- Training signal for future tuning
- Session summarization

**Schema Fields**:
- `summary` (high-level description of what happened)
- `raw_state` (serialized messages or tool outputs)
- `timestamp`
- Linked by `session_id`, `user_id`, `realm_id`, `case_id`

```python
self.persist_episodic_memory(..., summary=response["messages"][-1].content, raw_state=processed_response)
```

---

### Semantic Memory

**Purpose**:  Stores **discrete facts, inferences, and world knowledge** collected from sessions or external sources.

**Think of it as**: The "knowledge base" or "fact memory" for the agent.

**Use Cases**:
- Fact recall across sessions
- Integrate with vector databases for retrieval-augmented generation (RAG)
- Knowledge grounding and conditioning

**Schema Fields**:
- `key`, `value` (knowledge pairs)
- `vector` (embedding vector for similarity search)
- `tags` (e.g., ["underwriting", "fraud"])
- `source` (e.g., tool, user, knowledge base)

```python
self.persist_semantic_memory(..., key="credit_score", value="low", tags=["risk"], vector=[...])
```

---

### Procedural Memory

**Purpose**: Encodes **task flows**, **workflow steps**, and **trigger conditions** followed by the agent during its operation.

**Think of it as**: The "skill memory" or "how-to" knowledge—how the agent completed a task.

**Use Cases**:
- Reproducibility of logic paths
- Debugging and behavioral analysis
- Task graph evolution and monitoring

**Schema Fields**:
- `task_name`
- `steps` (list of strings or JSON steps)
- `trigger_conditions` (when/how to execute)
- Linked by `case_id` and `created_by`

```python
self.persist_procedural_memory(..., task_name="document_verification_task", steps=["fetch-doc", "ocr-parse"])
```

---

## Agent Orchestration (Multi-Agent)
This system uses LangGraph, a graph-based orchestration framework from LangChain, to manage interactions between multiple agents. Each agent operates independently, handling a specific task within a larger workflow and communicating via shared memory and message-passing protocols


### LangGraph DAG
LangGraph provides a Directed Acyclic Graph (DAG) structure to model agent workflows. Each node in the graph represents an agent or a tool, and the edges define the transition logic between them.
Nodes represent either agents or tools (e.g., ReAct Agents, ToolNodes), while edges determine the conditional logic for transitions. LangGraph enables automatic retries, rollback behavior, and checkpointing. Redis is used as the main checkpointer with optional AWS S3 support for persistence

## Multi-Agents
The system includes several agents working together through LangGraph DAGs to process customer data, make decisions, and generate reports. Each agent has a distinct responsibility and is loosely coupled to ensure maintainability and scalability.

### Data Acqusition Agent
The Data Acquisition Agent is responsible for collecting data from various sources, including user-submitted inputs via APIs and prefill mechanisms from third-party services. Its primary role is to aggregate, standardize, and validate incoming data to ensure a consistent, structured format suitable for downstream agents in the pipeline. This agent marks the beginning of the processing flow and is critical for initializing user sessions. It stores the initial session state in Redis for fast, short-term access and in PostgreSQL for persistent long-term storage and auditing purposes.

### Document Validation and Tagging Agent
This agent processes uploaded documents, such as identity proofs, financial statements, or utility bills. It performs OCR, LLM-assisted tagging, and consistency checks between documents and user-submitted data. Once verified, it updates the semantic memory and flags discrepancies. It may re-trigger upstream or downstream agents based on tagging confidence or rule failures.

### Screening Operation Maker and Checkker
The Maker performs automated rule-based screening using LLMs or traditional rules engines. It classifies user profiles, flags risks, and prepares a preliminary risk profile. The Checker, often a human-in-the-loop, verifies or overrides these decisions based on domain expertise. This dual-control pattern (Maker-Checker) ensures both speed and accountability in high-risk decisions.

### Screening Operation (Human-in-A-Loop)
When automated agents reach a confidence threshold below acceptable limits or when flagged manually, this agent collects inputs from human operators. It surfaces all relevant context—conversation history, memory snapshots, document extracts—so humans can make informed decisions. Feedback from these sessions is stored for training and agent improvement.

### Underwriting and Lender Seslection Agent
This agent calculates eligibility, evaluates risk scores, and matches the user profile to available lender products. It considers constraints like loan amount, rate of interest, tenure, and user category. All procedural steps are logged, and any overrides or escalations are recorded in procedural and episodic memory. Final lender selections are passed to the reporting pipeline.

### Reporting Agent
The Reporting Agent aggregates logs, trace information from Langfuse, and agent outputs to generate human-readable reports. These reports are stored in ClickHouse and PostgreSQL for real-time analytics and regulatory compliance. The agent also supports dashboard generation and alerting for operational teams.
