
import streamlit as st
import pandas as pd

from frontend.api_client import api_get


# -----------------------------------------
# FETCH MONITORING DATA
# -----------------------------------------

def fetch_monitoring_data():

    try:

        response = api_get(
            "/api/monitoring/summary",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        error_message = str(error)

        if getattr(error, "response", None) is not None:

            try:

                error_message = error.response.json().get(
                    "detail",
                    error_message
                )

            except (ValueError, AttributeError):
                pass

        st.error(
            f"Monitoring API Error: {error_message}"
        )

        return None


# -----------------------------------------
# REQUEST METRICS
# -----------------------------------------

def render_request_metrics(data):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Requests",
        data.get("total_requests", 0)
    )

    col2.metric(
        "Successful Requests",
        data.get("successful_requests", 0)
    )

    col3.metric(
        "Failed Requests",
        data.get("failed_requests", 0)
    )

    col4.metric(
        "Average Response Time",
        f'{data.get("average_response_time_ms", 0)} ms'
    )

    st.caption(
        f'Records analyzed: {data.get("records_analyzed", 0)} '
        f'of {data.get("total_requests", 0)} stored requests.'
    )


# -----------------------------------------
# DAILY ANALYTICS
# -----------------------------------------

def render_daily_analytics(data):

    st.subheader("📅 Daily Request Analytics")

    daily_records = data.get(
        "daily_statistics",
        []
    )

    if not daily_records:

        st.info(
            "No daily API analytics available yet."
        )

        return

    df = pd.DataFrame(daily_records)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        "date"
    ).set_index("date")

    st.line_chart(
        df[["requests", "failed"]],
        use_container_width=True
    )

    st.dataframe(
        df.reset_index(),
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------------
# ENDPOINT STATISTICS
# -----------------------------------------

def render_endpoint_statistics(data):

    st.subheader("Endpoint Performance")

    endpoints = data.get(
        "endpoint_statistics",
        []
    )

    if not endpoints:

        st.info(
            "No API requests recorded yet."
        )

        return

    df = pd.DataFrame(endpoints)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    if "endpoint" in df.columns and "request_count" in df.columns:

        chart_data = df.set_index(
            "endpoint"
        )["request_count"]

        st.subheader("Requests by Endpoint")

        st.bar_chart(chart_data)


# -----------------------------------------
# SLOW REQUESTS
# -----------------------------------------

def render_slow_requests(data):

    st.subheader("🐢 Slow API Requests")

    slow_requests = data.get(
        "slow_requests",
        []
    )

    if not slow_requests:

        st.success(
            "No slow requests recorded."
        )

        return

    df = pd.DataFrame(slow_requests)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------------
# ERROR HISTORY
# -----------------------------------------

def render_error_history(data):

    st.subheader("🚨 Recent API Errors")

    errors = data.get(
        "recent_errors",
        []
    )

    if not errors:

        st.success(
            "No failed API requests recorded."
        )

        return

    df = pd.DataFrame(errors)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------------
# RECENT REQUESTS
# -----------------------------------------

def render_recent_requests(data):

    st.subheader("Recent API Requests")

    requests_data = data.get(
        "recent_requests",
        []
    )

    if not requests_data:

        st.info(
            "No requests recorded yet."
        )

        return

    df = pd.DataFrame(requests_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Request Logs CSV",
        data=csv_data,
        file_name="api_request_logs.csv",
        mime="text/csv"
    )


# -----------------------------------------
# MAIN API MONITORING VIEW
# -----------------------------------------

def render_api_monitoring_view():

    st.title("📈 API Performance Monitoring")

    st.write(
        "Monitor API traffic, historical performance, "
        "response times and HTTP errors."
    )

    if st.button("🔄 Refresh Monitoring Data"):

        st.rerun()

    data = fetch_monitoring_data()

    if data is None:

        return

    render_request_metrics(data)

    st.divider()

    render_daily_analytics(data)

    st.divider()

    render_endpoint_statistics(data)

    st.divider()

    render_slow_requests(data)

    st.divider()

    render_error_history(data)

    st.divider()

    render_recent_requests(data)
