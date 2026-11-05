
import streamlit as st
import plotly.express as px
import pandas as pd


# -----------------------------------------
# TICKET STATUS CHART
# -----------------------------------------

def render_ticket_chart(ticket_data=None):

    st.subheader("📊 Ticket Analytics")

    if ticket_data is None:
        ticket_data = {
            "Status": ["Resolved", "Pending", "Escalated"],
            "Count": [0, 0, 0]
        }

    df = pd.DataFrame(ticket_data)

    fig = px.bar(
        df,
        x="Status",
        y="Count",
        title="Ticket Status Overview",
        text="Count"
    )

    fig.update_layout(
        xaxis_title="Ticket Status",
        yaxis_title="Number of Tickets",
        showlegend=False
    )

    st.plotly_chart(fig, width="stretch")


# -----------------------------------------
# AGENT PERFORMANCE CHART
# -----------------------------------------

def render_agent_chart(agent_data=None):

    st.subheader("🤖 Agent Performance")

    if agent_data is None:
        agent_data = {
            "Agent": [
                "Intake",
                "Intent",
                "Investigation",
                "Policy",
                "Resolution",
                "Compliance",
                "Escalation"
            ],
            "Tasks": [0, 0, 0, 0, 0, 0, 0]
        }

    df = pd.DataFrame(agent_data)

    fig = px.bar(
        df,
        x="Agent",
        y="Tasks",
        title="Agent Task Distribution",
        text="Tasks"
    )

    fig.update_layout(
        xaxis_title="Agent",
        yaxis_title="Number of Tasks"
    )

    st.plotly_chart(fig, width="stretch")


# -----------------------------------------
# CONVERSATION TREND CHART
# -----------------------------------------

def render_conversation_trend(conversation_data=None):

    st.subheader("💬 Conversation Analytics")

    if not conversation_data:

        st.info(
            "No conversation history available for trend analysis."
        )

        return

    df = pd.DataFrame(conversation_data)

    if df.empty or "created_at" not in df.columns:

        st.info("Conversation date information is unavailable.")

        return

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
        utc=True
    )

    df = df.dropna(subset=["created_at"])

    if df.empty:

        st.info("No valid conversation dates found.")

        return

    df["Date"] = (
        df["created_at"]
        .dt.tz_convert(None)
        .dt.date
    )

    trend_df = (
        df.groupby("Date")
        .size()
        .reset_index(name="Conversations")
        .sort_values("Date")
    )

    fig = px.line(
        trend_df,
        x="Date",
        y="Conversations",
        markers=True,
        title="Daily Conversation Trend"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Conversations"
    )

    st.plotly_chart(fig, width="stretch")
