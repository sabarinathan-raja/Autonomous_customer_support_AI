
import streamlit as st


def render_metric_cards(
    total_tickets=0,
    resolved_tickets=0,
    pending_tickets=0,
    escalated_tickets=0,
    total_conversations=0,
    average_evaluation_score=0.0
):

    st.subheader("📊 Support Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Conversations",
            value=total_conversations
        )

    with col2:
        st.metric(
            label="Total Tickets",
            value=total_tickets
        )

    with col3:
        st.metric(
            label="Average Evaluation Score",
            value=f"{average_evaluation_score:.4f}"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            label="Resolved Tickets",
            value=resolved_tickets
        )

    with col5:
        st.metric(
            label="Pending Tickets",
            value=pending_tickets
        )

    with col6:
        st.metric(
            label="Escalated Tickets",
            value=escalated_tickets
        )
