
import streamlit as st


AGENTS = [
    {
        "name": "Intake Agent",
        "description": "Receives and understands customer requests.",
        "icon": "📩"
    },
    {
        "name": "Intent Agent",
        "description": "Identifies customer intent and priority.",
        "icon": "🎯"
    },
    {
        "name": "Investigation Agent",
        "description": "Investigates customer order information.",
        "icon": "🔍"
    },
    {
        "name": "Policy Retrieval Agent",
        "description": "Retrieves relevant policies using RAG.",
        "icon": "📚"
    },
    {
        "name": "Resolution Agent",
        "description": "Generates a policy-grounded response.",
        "icon": "🤖"
    },
    {
        "name": "Compliance Agent",
        "description": "Validates response and evidence.",
        "icon": "🛡️"
    },
    {
        "name": "Escalation Agent",
        "description": "Evaluates human support requirements.",
        "icon": "🚨"
    },
    {
        "name": "Final Response Agent",
        "description": "Generates the final customer response.",
        "icon": "💬"
    }
]


def render_agent_status(statuses=None):

    st.subheader("⚙️ Multi-Agent Status")

    st.caption(
        "Eight specialized agents in the customer support workflow."
    )

    statuses = statuses or {}

    columns = st.columns(3)

    for index, agent in enumerate(AGENTS):

        status = statuses.get(
            agent["name"],
            "Not Started"
        )

        with columns[index % 3]:

            with st.container(border=True):

                st.markdown(
                    f"### {agent['icon']} {agent['name']}"
                )

                st.caption(agent["description"])

                if status.lower() == "completed":
                    st.success("Completed")

                elif status.lower() == "running":
                    st.info("Running")

                elif status.lower() == "failed":
                    st.error("Failed")

                else:
                    st.warning("Not Started")
