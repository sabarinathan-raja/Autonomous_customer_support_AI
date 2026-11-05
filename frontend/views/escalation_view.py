import streamlit as st

from frontend.api_client import api_get

from frontend.components.escalation_panel import render_escalation_panel


def render_escalation_view():

    st.title(" Human Escalation Management")

    try:

        response = api_get(
            "/api/escalations",
            timeout=10
        )

        response.raise_for_status()

        escalations = response.json()

        st.metric(
            "Total Escalations",
            len(escalations)
        )

        if escalations:
            render_escalation_panel(escalations)
        else:
            st.success("No pending human escalations.")

    except Exception as error:

        st.error(f"Escalation API error: {error}")