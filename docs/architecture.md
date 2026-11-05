# System Architecture

```mermaid
flowchart TD
    A[Customer] --> B[Streamlit Frontend]
    B --> C[FastAPI Backend]
    C --> D[Guardrails]
    D --> E[Multi-Agent Workflow]

    E --> F[Intake Agent]
    F --> G[Intent Agent]
    G --> H[Investigation Agent]
    G --> I[Policy Agent]

    H --> J[Resolution Agent]
    I --> J

    J --> K[Compliance Validation]
    K --> L{Escalation Required?}

    L -->|No| M[Customer Response]
    L -->|Yes| N[Human Escalation]

    M --> O[Ticket History]
    N --> O