import streamlit as st
import pandas as pd

from frontend.api_client import api_get

from frontend.components.agent_status import render_agent_status
from frontend.components.workflow import render_workflow


AGENT_NAME_MAP = {
    "intake agent": "Intake Agent",
    "intent agent": "Intent Agent",
    "investigation agent": "Investigation Agent",
    "policy retrieval agent": "Policy Retrieval Agent",
    "resolution agent": "Resolution Agent",
    "compliance agent": "Compliance Agent",
    "escalation agent": "Escalation Agent",
    "final response agent": "Final Response Agent",
}


def render_agents_view():

    st.title("🤖 AI Agents")

    try:

        response = api_get(
            "/api/audit-logs",
            timeout=10
        )

        response.raise_for_status()

        logs = response.json()

        if not logs:
            st.info("No agent execution records found.")
            render_agent_status()
            return

        df = pd.DataFrame(logs)

        required_columns = [
            "case_id",
            "agent_name",
            "status",
            "created_at"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            st.error(
                f"Missing API columns: {missing_columns}"
            )
            return

        df["case_id"] = df["case_id"].astype(str).str.strip()

        df["agent_name_normalized"] = (
            df["agent_name"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["agent_name_display"] = (
            df["agent_name_normalized"]
            .map(AGENT_NAME_MAP)
        )

        case_ids = sorted(
            df.loc[
                df["case_id"].ne(""),
                "case_id"
            ].dropna().unique().tolist(),
            reverse=True
        )

        if not case_ids:
            st.warning("No Case IDs available.")
            return

        selected_case = st.selectbox(
            "Select Customer Case",
            case_ids
        )

        case_df = df[
            df["case_id"] == selected_case
        ].copy()

        case_df["created_at"] = pd.to_datetime(
            case_df["created_at"],
            errors="coerce",
            utc=True
        )

        case_df = case_df.sort_values(
            "created_at",
            na_position="first"
        )

        latest_logs = case_df.drop_duplicates(
            subset=["agent_name_normalized"],
            keep="last"
        )

        statuses = {}

        for _, record in latest_logs.iterrows():

            agent_name = record["agent_name_display"]

            if not agent_name:
                continue

            status = str(record["status"]).strip().lower()

            if status == "success":
                statuses[agent_name] = "Completed"

            elif status == "failed":
                statuses[agent_name] = "Failed"

            elif status == "running":
                statuses[agent_name] = "Running"

        # Case Information
        st.subheader("📌 Case Information")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Selected Case", selected_case)

        with col2:
            ticket_ids = (
                case_df["ticket_id"].dropna()
                if "ticket_id" in case_df.columns
                else pd.Series(dtype=str)
            )

            ticket_id = (
                ticket_ids.iloc[-1]
                if not ticket_ids.empty
                else "Not Linked"
            )

            st.metric("Ticket ID", ticket_id)

        st.divider()

        # Agent Status
        render_agent_status(statuses)

        st.divider()

        # Execution Summary
        st.subheader("📊 Agent Execution Summary")

        col1, col2, col3 = st.columns(3)

        completed_count = list(
            statuses.values()
        ).count("Completed")

        failed_count = list(
            statuses.values()
        ).count("Failed")

        with col1:
            st.metric(
                "Executed Agents",
                len(statuses)
            )

        with col2:
            st.metric(
                "Completed",
                completed_count
            )

        with col3:
            st.metric(
                "Failed",
                failed_count
            )

        # Workflow
        st.divider()
        st.subheader("🔄 Multi-Agent Workflow")

        workflow_order = [
            "Intake Agent",
            "Intent Agent",
            "Investigation Agent",
            "Policy Retrieval Agent",
            "Resolution Agent",
            "Compliance Agent",
            "Escalation Agent",
            "Final Response Agent"
        ]

        for agent_name in workflow_order:

            status = statuses.get(
                agent_name,
                "Not Started"
            )

            if status == "Completed":
                st.success(f"✓ {agent_name} — Completed")

            elif status == "Failed":
                st.error(f"✗ {agent_name} — Failed")

            elif status == "Running":
                st.info(f"● {agent_name} — Running")

            else:
                st.warning(f"○ {agent_name} — Not Started")

        # Execution Details
        st.divider()
        st.subheader("⏱️ Agent Execution Details")

        display_columns = [
            "agent_name",
            "status",
            "execution_time",
            "created_at",
            "details"
        ]

        available_columns = [
            column for column in display_columns
            if column in case_df.columns
        ]

        st.dataframe(
            case_df[available_columns],
            use_container_width=True,
            hide_index=True
        )

        # Diagnostic information
        with st.expander("🔍 Debug Agent Records"):

            st.write(
                "Raw agent names and statuses for this Case ID:"
            )

            debug_columns = [
                "case_id",
                "agent_name",
                "status",
                "ticket_id"
            ]

            debug_columns = [
                col for col in debug_columns
                if col in case_df.columns
            ]

            st.dataframe(
                case_df[debug_columns],
                use_container_width=True,
                hide_index=True
            )

            if "Intake Agent" not in statuses:
                st.warning(
                    "Intake Agent record was not found "
                    "for this Case ID. Check the backend "
                    "audit log Case ID."
                )

    except Exception as error:

        st.error(
            f"Agent Dashboard Error: {error}"
        )