# 🚀 Autonomous Customer Support AI
### An Intelligent Multi-Agent Customer Support Automation Platform

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)

## 📌 Project Overview

**Autonomous Customer Support AI** is a business-oriented AI-powered customer support automation platform designed to streamline customer service operations through multi-agent collaboration, Retrieval-Augmented Generation (RAG), policy validation, and intelligent workflow orchestration.

The system uses specialized AI agents to understand customer requests, investigate order-related issues, retrieve relevant business policies, generate context-aware responses, validate compliance, and escalate complex cases to human support teams.

Unlike traditional rule-based chatbots, this solution follows a modular multi-agent architecture to support structured decision-making and reliable customer support workflows.

## 🎯 Business Problem

Traditional customer support operations often face challenges such as:

- High volumes of repetitive customer queries.
- Manual order investigation and verification.
- Difficulty retrieving relevant business policies.
- Inconsistent customer responses.
- Delayed issue resolution.
- Limited visibility into support operations.

## 💡 Proposed Solution

This project introduces an AI-driven multi-agent system that automates important customer support activities while maintaining policy awareness and human oversight.

The platform combines specialized agents, RAG-based knowledge retrieval, conversation memory, compliance validation, and human escalation to support customer service workflows.

## 🏗️ System Architecture

The platform follows a layered architecture consisting of:

1. **Frontend Layer:** Streamlit-based customer support interface.
2. **API Layer:** FastAPI backend for request handling and service communication.
3. **Guardrails Layer:** Input validation, prompt injection checks, safety checks, policy validation, and output validation.
4. **Multi-Agent Layer:** LangGraph-based workflow orchestration.
5. **Knowledge Layer:** RAG-based retrieval from business policy documents.
6. **Memory Layer:** Conversation history and case context management.
7. **Evaluation Layer:** Response quality evaluation, monitoring, and logging.
8. **Deployment Layer:** Docker and Docker Compose.

## 🤖 Multi-Agent Workflow

The system contains specialized agents with separate responsibilities.

| Agent | Responsibility |
|---|---|
| Intake Agent | Extracts customer information and order details |
| Intent Agent | Classifies customer intent and priority |
| Investigation Agent | Investigates order information |
| Policy Agent | Retrieves relevant business policies |
| Resolution Agent | Generates context-aware resolutions |
| Compliance Agent | Validates responses against policy evidence and verified information |
| Escalation Agent | Determines whether human intervention is required |

### Workflow Execution

Customer Request → Intake → Intent Classification → Order Investigation → Policy Retrieval → Resolution Generation → Compliance Validation → Escalation Decision → Final Response

## 📚 RAG Knowledge System

The Retrieval-Augmented Generation component helps the system generate responses using relevant business knowledge.

Key capabilities:

- Business policy document ingestion.
- Document processing and retrieval.
- Context-aware information retrieval.
- Policy-grounded response generation.
- Evidence-based response validation.

## 🛡️ AI Guardrails & Security

The platform includes guardrail components designed to improve safe and controlled AI interactions.

- Input validation.
- Prompt injection pattern detection.
- Output validation.
- Sensitive information request checks.
- Basic safety checks.
- Policy compliance validation.
- API key authentication.
- Rate limiting.
- CORS configuration.

## 🧠 Conversation Memory

The system maintains conversation context to support multi-turn customer interactions.

- Conversation history.
- Customer case context.
- Order ID continuity.
- Context-aware support interactions.

## 📊 Evaluation & Monitoring

The platform includes capabilities for monitoring system performance and evaluating AI responses.

- Response quality evaluation.
- API performance monitoring.
- Request and error tracking.
- Agent execution monitoring.
- Audit logs.
- Evaluation history.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| Agent Orchestration | LangGraph |
| AI / LLM | Gemini |
| AI Architecture | Multi-Agent Systems |
| Knowledge Retrieval | RAG |
| Database | SQLite, SQLAlchemy |
| API Communication | REST API |
| Security | API Key Authentication, Rate Limiting, CORS |
| Testing | Pytest |
| Deployment | Docker, Docker Compose |

## 📁 Project Structure

```text
Autonomous_Customer_Support/
│
├── backend/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── graph/
│   ├── guardrails/
│   ├── mcp/
│   ├── models/
│   ├── rag/
│   ├── services/
│   ├── client.py
│   └── main.py
│
├── data/
│   ├── policies/
│   ├── orders/
│   └── vectorstore/
│
├── frontend/
│   ├── components/
│   ├── views/
│   └── styles.py
│
├── tests/
├── evaluation/
├── logs/
├── .streamlit/
│
├── .env.example
├── .gitignore
├── app.py
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.11 or compatible Python environment.
- Git.
- Docker Desktop (for containerized deployment).
- Gemini API Key.

### 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

```bash
cd Autonomous_Customer_Support
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

DATABASE_URL=sqlite:///./customer_support.db

API_KEY=your_random_secure_api_key

API_HOST=127.0.0.1
API_PORT=8000
API_BASE_URL=http://127.0.0.1:8000

RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60

CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

**Security:** Never commit `.env` or real API keys to GitHub. Use `.env.example` with placeholder values.

### 5. Start Backend

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start Frontend

Open another terminal:

```bash
streamlit run app.py
```

Frontend:

```text
http://localhost:8501
```

## 🐳 Docker Deployment

Build Docker images:

```bash
docker compose build
```

Start the application:

```bash
docker compose up -d
```

Check containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop containers:

```bash
docker compose down
```

## 🧪 Testing

Run the Guardrails test suite:

```bash
python -m pytest tests/test_guardrails.py -v
```

Run all project tests:

```bash
python -m pytest tests/ -v
```

## 📈 Business Value

This project demonstrates how Agentic AI can support business customer service operations through:

- Reduced repetitive manual support activities.
- More consistent policy-aware responses.
- Structured order investigation.
- Context-aware customer interactions.
- Human intervention for complex cases.
- Improved operational monitoring and visibility.

## 🔮 Future Enhancements

- Advanced prompt injection detection.
- Dedicated PII detection and redaction.
- Stronger hallucination detection.
- Distributed rate limiting.
- Persistent security event auditing.
- Advanced agent observability.
- Cloud deployment and scalability improvements.
- Integration with CRM and enterprise ticketing platforms.

## 👨‍💻 Project Focus

This project focuses on applying Generative AI, Agentic AI, RAG, backend engineering, workflow orchestration, application security, and containerization to a practical business problem.

**Building intelligent AI systems that go beyond answering questions — systems designed to understand, investigate, validate, and resolve customer support requests.**

---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback.

#AgenticAI #GenerativeAI #MultiAgentSystems #RAG #LangGraph #FastAPI #Python #EnterpriseAI #Docker #CustomerSupportAutomation