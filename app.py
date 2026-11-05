import streamlit as st

from frontend.styles import load_custom_styles
from frontend.components.header import render_header
from frontend.components.sidebar import render_sidebar

from frontend.views.dashboard_view import render_dashboard
from frontend.views.chat_view import render_chat_view
from frontend.views.tickets_view import render_tickets_view
from frontend.views.agents_view import render_agents_view
from frontend.views.audit_view import render_audit_view
from frontend.views.evaluation_view import render_evaluation_view
from frontend.views.analytics_view import render_analytics_view
from frontend.views.escalation_view import render_escalation_view
from frontend.views.health_view import render_health_view
from frontend.views.api_monitoring_view import render_api_monitoring_view


st.set_page_config(
    page_title="Autonomous Customer Support AI",
    page_icon="🤖",
    layout="wide"
)

load_custom_styles()

render_header()

selected_page = render_sidebar()

if selected_page == "Dashboard":
    render_dashboard()

elif selected_page == "Customer Chat":
    render_chat_view()

elif selected_page == "Tickets":
    render_tickets_view()

elif selected_page == "Agents":
    render_agents_view()

elif selected_page == "Escalation":
    render_escalation_view()

elif selected_page == "Evaluation":
    render_evaluation_view()

elif selected_page == "Analytics":
    render_analytics_view()

elif selected_page == "Audit":
    render_audit_view()

elif selected_page == "Health":
    render_health_view()

elif selected_page == "API Monitoring":
    render_api_monitoring_view()