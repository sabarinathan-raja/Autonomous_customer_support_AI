
import streamlit as st


WORKFLOW_STEPS = [
    "Intake Agent",
    "Intent Agent",
    "Investigation Agent",
    "Policy Retrieval Agent",
    "Resolution Agent",
    "Compliance Agent",
    "Escalation Agent",
    "Final Response Agent"
]


def render_workflow(statuses=None):

    st.subheader("🔄 Multi-Agent Workflow")

    st.caption(
        "Customer request processing pipeline"
    )

    statuses = statuses or {}

    for index, step in enumerate(WORKFLOW_STEPS):

        status = statuses.get(step, "Not Started")

        col1, col2 = st.columns([1, 5])

        with col1:

            if status == "Completed":
                st.success("✓")

            elif status == "Failed":
                st.error("✕")

            elif status == "Running":
                st.info("●")

            else:
                st.warning("○")

        with col2:

            if status == "Completed":
                st.markdown(f"**{step} — Completed**")

            elif status == "Failed":
                st.markdown(f"**{step} — Failed**")

            elif status == "Running":
                st.markdown(f"**{step} — Running**")

            else:
                st.markdown(f"{step} — Pending")

        if index < len(WORKFLOW_STEPS) - 1:
            st.markdown("│")
