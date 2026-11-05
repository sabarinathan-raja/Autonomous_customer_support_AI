import streamlit as st

from frontend.api_client import api_get

from frontend.components.cards import render_metric_cards
from frontend.components.charts import render_ticket_chart


def render_analytics_view():

    st.title("📊 Analytics")

    try:

        response = api_get(
            "/api/dashboard/summary",
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        total_tickets = data.get("total_tickets", 0)
        resolved_tickets = data.get("resolved_tickets", 0)
        pending_tickets = data.get("pending_tickets", 0)
        escalated_tickets = data.get("escalated_tickets", 0)

        # Display actual backend metrics
        render_metric_cards(
            total_tickets=total_tickets,
            resolved_tickets=resolved_tickets,
            pending_tickets=pending_tickets,
            escalated_tickets=escalated_tickets
        )

        # Display actual ticket status chart
        ticket_data = {
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
        }

        render_ticket_chart(ticket_data)

    except Exception as error:

        st.error(
            f"Analytics loading failed: {error}"
        )