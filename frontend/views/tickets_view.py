import streamlit as st

from frontend.api_client import api_get

from frontend.components.ticket_panel import render_ticket_panel


def render_tickets_view():

    st.title("Ticket Management")

    try:

        response = api_get(
            "/api/tickets",
            timeout=10
        )

        response.raise_for_status()

        tickets = response.json()

        st.metric("Total Tickets", len(tickets))

        if tickets:
            render_ticket_panel(tickets)
        else:
            st.info("No tickets available.")

    except Exception as error:

        st.error(f"Unable to load tickets: {error}")