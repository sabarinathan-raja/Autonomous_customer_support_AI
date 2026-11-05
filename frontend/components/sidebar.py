import streamlit as st


def render_sidebar():

    st.sidebar.title("🎛️ Navigation")

    selected_page = st.sidebar.radio(
        "Select Page",
        [
            "Dashboard",
            "Customer Chat",
            "Tickets",
            "Agents",
            "Escalation",
            "Audit",
            "Evaluation",
            "Analytics",
            "Health",
            "API Monitoring"
        ]
    )

    st.sidebar.divider()

    st.sidebar.subheader("System Information")

    st.sidebar.info("Backend: FastAPI")
    st.sidebar.info("Workflow: LangGraph")
    st.sidebar.info("Knowledge Base: RAG")
    st.sidebar.info("LLM: Gemini")

    st.sidebar.divider()

    st.sidebar.caption(
        "Autonomous Customer Support AI | Version 1.0"
    )

    return selected_page