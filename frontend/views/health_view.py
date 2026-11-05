import streamlit as st
import pandas as pd

from frontend.api_client import api_get


def fetch_health_status():

    try:

        response = api_get(
            "/health",
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        st.error(f"Health Check API Error: {error}")

        return None


def render_service_card(service_name, service_data):

    status = service_data.get("status", "unknown")

    message = service_data.get(
        "message",
        "No information"
    )

    with st.container(border=True):

        if status in ["healthy", "available"]:

            st.success(
                f"🟢 {service_name}: {status.upper()}"
            )

        elif status == "degraded":

            st.warning(
                f"🟡 {service_name}: {status.upper()}"
            )

        else:

            st.error(
                f"🔴 {service_name}: {status.upper()}"
            )

        st.caption(message)

        response_time = service_data.get(
            "response_time_ms"
        )

        if response_time is not None:

            st.caption(
                f"Response Time: {response_time} ms"
            )


def render_health_view():

    st.title("🩺 System Health Monitoring")

    st.write(
        "Monitor the availability of your Customer Support AI services."
    )

    if st.button("🔄 Refresh Health Status"):

        st.rerun()

    health_data = fetch_health_status()

    if not health_data:

        st.error(
            "Unable to retrieve system health information."
        )

        return

    overall_status = health_data.get(
        "status",
        "unknown"
    )

    st.subheader("Overall System Status")

    if overall_status == "healthy":

        st.success(
            "🟢 All monitored services are healthy."
        )

    else:

        st.warning(
            "🟡 System is degraded. Check the service details."
        )

    st.caption(
        f"Last Checked: {health_data.get('timestamp', 'N/A')}"
    )

    st.divider()

    st.subheader("Service Status")

    services = health_data.get("services", {})

    service_names = [
        ("API", "api"),
        ("Database", "database"),
        ("LangGraph Workflow", "workflow")
    ]

    columns = st.columns(3)

    for column, (display_name, service_key) in zip(
        columns,
        service_names
    ):

        with column:

            render_service_card(
                display_name,
                services.get(service_key, {})
            )

    st.divider()

    st.subheader("Detailed Health Information")

    details = []

    for service_name, service_data in services.items():

        details.append({
            "Service": service_name.replace(
                "_", " "
            ).title(),

            "Status": service_data.get(
                "status",
                "unknown"
            ),

            "Message": service_data.get(
                "message",
                "N/A"
            ),

            "Response Time (ms)": service_data.get(
                "response_time_ms",
                "N/A"
            )
        })

    if details:

        st.dataframe(
            pd.DataFrame(details),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("System Information")

    col1, col2 = st.columns(2)

    with col1:

        st.info("Backend Framework: FastAPI")

        st.info("Workflow Engine: LangGraph")

    with col2:

        st.info("Database: SQLAlchemy")

        st.info("Frontend: Streamlit")