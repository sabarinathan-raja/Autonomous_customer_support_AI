import streamlit as st

from frontend.api_client import api_get

from frontend.components.cards import render_metric_cards
from frontend.components.agent_status import render_agent_status
from frontend.components.charts import (
    render_ticket_chart,
    render_conversation_trend
)


# -----------------------------------------
# API HELPER
# -----------------------------------------

def fetch_api_data(endpoint):

    try:

        response = api_get(
            endpoint,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        st.error(f"API error ({endpoint}): {error}")

        return None


# -----------------------------------------
# EVALUATION SCORE CALCULATION
# -----------------------------------------

def calculate_average_evaluation(evaluations):

    if not evaluations:
        return 0.0

    scores = []

    for item in evaluations:

        score = item.get("overall_score")

        if score is None:
            continue

        try:

            scores.append(float(score))

        except (TypeError, ValueError):

            continue

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


# -----------------------------------------
# MAIN DASHBOARD
# -----------------------------------------

def render_dashboard():

    st.title("📊 Customer Support AI Dashboard")

    st.caption(
        "Monitor support tickets, conversations and AI response quality."
    )

    # -----------------------------------------
    # LOAD DASHBOARD SUMMARY
    # -----------------------------------------

    dashboard_data = fetch_api_data(
        "/api/dashboard/summary"
    )

    # -----------------------------------------
    # LOAD CONVERSATIONS
    # -----------------------------------------

    conversation_data = fetch_api_data(
        "/api/conversations"
    )

    # -----------------------------------------
    # LOAD EVALUATION HISTORY
    # -----------------------------------------

    evaluation_data = fetch_api_data(
        "/api/evaluation/history"
    )

    if not isinstance(dashboard_data, dict):

        st.warning(
            "Dashboard summary could not be loaded."
        )

        return

    if not isinstance(conversation_data, list):
        conversation_data = []

    if not isinstance(evaluation_data, list):
        evaluation_data = []

    # -----------------------------------------
    # CALCULATE METRICS
    # -----------------------------------------

    total_conversations = len(conversation_data)

    average_evaluation_score = calculate_average_evaluation(
        evaluation_data
    )

    total_tickets = dashboard_data.get(
        "total_tickets",
        0
    )

    resolved_tickets = dashboard_data.get(
        "resolved_tickets",
        0
    )

    pending_tickets = dashboard_data.get(
        "pending_tickets",
        0
    )

    escalated_tickets = dashboard_data.get(
        "escalated_tickets",
        0
    )

    # -----------------------------------------
    # METRIC CARDS
    # -----------------------------------------

    render_metric_cards(
        total_tickets=total_tickets,
        resolved_tickets=resolved_tickets,
        pending_tickets=pending_tickets,
        escalated_tickets=escalated_tickets,
        total_conversations=total_conversations,
        average_evaluation_score=average_evaluation_score
    )

    st.divider()

    # -----------------------------------------
    # TICKET STATUS ANALYTICS
    # -----------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        render_ticket_chart({
            "Status": [
                "Resolved",
                "Pending",
                "Escalated"
            ],
            "Count": [
                resolved_tickets,
                pending_tickets,
                escalated_tickets
            ]
        })

    with col2:

        st.subheader("📈 Ticket Distribution")

        if total_tickets > 0:

            import plotly.express as px
            import pandas as pd

            status_df = pd.DataFrame({
                "Status": [
                    "Resolved",
                    "Pending",
                    "Escalated"
                ],
                "Count": [
                    resolved_tickets,
                    pending_tickets,
                    escalated_tickets
                ]
            })

            status_df = status_df[
                status_df["Count"] > 0
            ]

            if not status_df.empty:

                fig = px.pie(
                    status_df,
                    names="Status",
                    values="Count",
                    title="Ticket Status Distribution",
                    hole=0.4
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )

            else:

                st.info("No ticket status data available.")

        else:

            st.info("No tickets available.")

    st.divider()

    # -----------------------------------------
    # CONVERSATION TREND
    # -----------------------------------------

    render_conversation_trend(
        conversation_data
    )

    st.divider()

    # -----------------------------------------
    # AI AGENT STATUS
    # -----------------------------------------

    st.subheader("🤖 AI Agent Monitoring")

    render_agent_status()

    st.divider()

    # -----------------------------------------
    # EVALUATION OVERVIEW
    # -----------------------------------------

    st.subheader("🧠 AI Response Quality")

    if evaluation_data:

        st.metric(
            "Total Evaluations",
            len(evaluation_data)
        )

        score_values = [
            item.get("overall_score")
            for item in evaluation_data
            if item.get("overall_score") is not None
        ]

        if score_values:

            st.caption(
                "Average score is calculated from saved overall evaluation scores."
            )

            st.progress(
                min(max(average_evaluation_score, 0.0), 1.0)
            )

        else:

            st.info(
                "Overall evaluation scores are not available."
            )

    else:

        st.info("No evaluation history available yet.")

    # -----------------------------------------
    # REFRESH DASHBOARD
    # -----------------------------------------

    if st.button("🔄 Refresh Dashboard"):

        st.rerun()