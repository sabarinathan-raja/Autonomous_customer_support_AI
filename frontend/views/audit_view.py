
import streamlit as st
import pandas as pd
import plotly.express as px

from frontend.api_client import api_get
# -----------------------------------------
# FETCH AUDIT LOGS
# -----------------------------------------

def fetch_audit_logs():

    try:

        response = api_get(
            "/api/audit-logs",
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data if isinstance(data, list) else []

    except Exception as error:

        st.error(f"Unable to fetch audit logs: {error}")

        return None
# -----------------------------------------
# PREPARE DATA
# -----------------------------------------

def prepare_audit_dataframe(logs):

    df = pd.DataFrame(logs)

    required_columns = [
        "id",
        "case_id",
        "ticket_id",
        "agent_name",
        "action",
        "status",
        "execution_time",
        "details",
        "created_at"
    ]

    for column in required_columns:

        if column not in df.columns:
            df[column] = None

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
        utc=True
    )

    df["execution_time"] = pd.to_numeric(
        df["execution_time"],
        errors="coerce"
    )

    df["status"] = (
        df["status"]
        .fillna("unknown")
        .astype(str)
        .str.lower()
    )

    return df


# -----------------------------------------
# SEARCH AUDIT LOGS
# -----------------------------------------

def filter_audit_logs(
    df,
    search_text,
    selected_agent,
    selected_status,
    start_date,
    end_date
):

    filtered_df = df.copy()

    if search_text:

        search_text = search_text.strip().lower()

        search_columns = [
            "case_id",
            "ticket_id",
            "agent_name",
            "action",
            "details"
        ]

        mask = pd.Series(
            False,
            index=filtered_df.index
        )

        for column in search_columns:

            mask |= (
                filtered_df[column]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    regex=False
                )
            )

        filtered_df = filtered_df[mask]

    if selected_agent != "All":

        filtered_df = filtered_df[
            filtered_df["agent_name"] == selected_agent
        ]

    if selected_status != "All":

        filtered_df = filtered_df[
            filtered_df["status"] == selected_status
        ]

    if start_date and end_date:

        local_dates = (
            filtered_df["created_at"]
            .dt.tz_convert(None)
            .dt.date
        )

        filtered_df = filtered_df[
            local_dates.between(
                start_date,
                end_date
            )
        ]

    return filtered_df


# -----------------------------------------
# EXECUTION METRICS
# -----------------------------------------

def render_execution_metrics(df):

    total = len(df)

    successful = int(
        (df["status"] == "success").sum()
    )

    failed = int(
        (df["status"] == "failed").sum()
    )

    other = total - successful - failed

    success_rate = (
        successful / total * 100
        if total else 0
    )

    average_time = df["execution_time"].mean()

    if pd.isna(average_time):
        average_time = 0

    st.subheader("📊 Agent Execution Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Executions", total)

    col2.metric("Successful", successful)

    col3.metric("Failed", failed)

    col4.metric("Other Status", other)

    col1, col2 = st.columns(2)

    col1.metric(
        "Success Rate",
        f"{success_rate:.2f}%"
    )

    col2.metric(
        "Average Execution Time",
        f"{average_time:.4f} sec"
    )


# -----------------------------------------
# AGENT PERFORMANCE
# -----------------------------------------

def render_agent_performance(df):

    st.subheader("🤖 Agent Performance Dashboard")

    if df.empty:

        st.info("No agent execution records available.")

        return

    agent_summary = (
        df.groupby("agent_name", dropna=False)
        .agg(
            total_executions=("id", "count"),
            successful_executions=(
                "status",
                lambda x: (x == "success").sum()
            ),
            failed_executions=(
                "status",
                lambda x: (x == "failed").sum()
            ),
            average_execution_time=(
                "execution_time",
                "mean"
            )
        )
        .reset_index()
    )

    agent_summary["agent_name"] = (
        agent_summary["agent_name"]
        .fillna("Unknown")
    )

    agent_summary["success_rate"] = (
        agent_summary["successful_executions"]
        / agent_summary["total_executions"]
        .replace(0, 1)
        * 100
    ).round(2)

    agent_summary["average_execution_time"] = (
        agent_summary["average_execution_time"]
        .round(4)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            agent_summary,
            x="agent_name",
            y="total_executions",
            title="Agent Execution Count",
            text="total_executions"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        fig = px.bar(
            agent_summary,
            x="agent_name",
            y="success_rate",
            title="Agent Success Rate",
            text="success_rate"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    fig = px.bar(
        agent_summary,
        x="agent_name",
        y="average_execution_time",
        title="Average Agent Execution Time",
        text="average_execution_time"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.subheader("Agent Performance Details")

    st.dataframe(
        agent_summary,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------------
# FAILURE ANALYSIS
# -----------------------------------------

def render_failure_analysis(df):

    st.subheader("🚨 Agent Failure Analysis")

    failed_df = df[
        df["status"] == "failed"
    ]

    total_failures = len(failed_df)

    failure_rate = (
        total_failures / len(df) * 100
        if len(df) else 0
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Failures",
        total_failures
    )

    col2.metric(
        "Failure Rate",
        f"{failure_rate:.2f}%"
    )

    if failed_df.empty:

        st.success("No agent failures found.")

    else:

        st.dataframe(
            failed_df[
                [
                    "id",
                    "case_id",
                    "ticket_id",
                    "agent_name",
                    "action",
                    "details",
                    "created_at"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# -----------------------------------------
# CASE EXECUTION TIMELINE
# -----------------------------------------

def render_case_timeline(df):

    st.subheader("🕒 Case Execution Timeline")

    case_ids = sorted(
        df["case_id"]
        .dropna()
        .unique()
        .tolist(),
        reverse=True
    )

    if not case_ids:

        st.info("No Case IDs available.")

        return

    selected_case = st.selectbox(
        "Select Case ID",
        case_ids,
        key="audit_case_timeline"
    )

    case_df = df[
        df["case_id"] == selected_case
    ].sort_values("created_at")

    st.caption(f"Case ID: {selected_case}")

    for _, record in case_df.iterrows():

        timestamp = record["created_at"]

        timestamp_text = (
            timestamp.strftime("%d-%m-%Y %H:%M:%S UTC")
            if pd.notna(timestamp)
            else "Time unavailable"
        )

        agent_name = record["agent_name"] or "Unknown"

        status = record["status"]

        with st.expander(
            f"{agent_name} | {status.upper()}"
        ):

            st.write(
                "**Action:**",
                record["action"]
            )

            execution_time = record["execution_time"]

            st.write(
                "**Execution Time:**",
                (
                    f"{execution_time:.4f} seconds"
                    if pd.notna(execution_time)
                    else "Unavailable"
                )
            )

            st.write(
                "**Timestamp:**",
                timestamp_text
            )

            st.write(
                "**Ticket ID:**",
                record["ticket_id"] or "Not linked"
            )

            st.write(
                "**Details:**",
                record["details"] or "No details"
            )


# -----------------------------------------
# AUDIT RECORD EXPORT
# -----------------------------------------

def render_audit_export(df):

    st.subheader("📥 Export Audit Logs")

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download Audit Logs CSV",
        data=csv_data,
        file_name="audit_logs.csv",
        mime="text/csv",
        use_container_width=True
    )


# -----------------------------------------
# MAIN AUDIT VIEW
# -----------------------------------------

def render_audit_view():

    st.title("📋 Audit Logs & Agent Monitoring")

    st.caption(
        "Monitor AI agent execution history, performance and failures."
    )

    if st.button("🔄 Refresh Audit Logs"):

        st.rerun()

    # -----------------------------------------
    # LOAD DATA
    # -----------------------------------------

    logs = fetch_audit_logs()

    if logs is None:
        return

    if not logs:

        st.info("No audit records found.")

        return

    df = prepare_audit_dataframe(logs)

    # -----------------------------------------
    # SEARCH AND FILTER
    # -----------------------------------------

    st.subheader("🔍 Search & Filter")

    col1, col2, col3 = st.columns(3)

    with col1:

        search_text = st.text_input(
            "Search Case ID / Ticket ID / Details",
            placeholder="Enter search value",
            key="audit_search"
        )

    with col2:

        agents = sorted(
            df["agent_name"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_agent = st.selectbox(
            "Filter by Agent",
            ["All"] + agents,
            key="audit_agent_filter"
        )

    with col3:

        statuses = sorted(
            df["status"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_status = st.selectbox(
            "Filter by Status",
            ["All"] + statuses,
            key="audit_status_filter"
        )

    # -----------------------------------------
    # DATE FILTER
    # -----------------------------------------

    st.subheader("📅 Date Filter")

    available_dates = (
        df["created_at"]
        .dropna()
        .dt.tz_convert(None)
        .dt.date
    )

    if not available_dates.empty:

        min_date = available_dates.min()
        max_date = available_dates.max()

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="audit_start_date"
            )

        with col2:

            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="audit_end_date"
            )

        if start_date > end_date:

            st.error("Start date cannot be after end date.")

            return

    else:

        start_date = None
        end_date = None

        st.info("Date information is unavailable.")

    # -----------------------------------------
    # APPLY FILTERS
    # -----------------------------------------

    filtered_df = filter_audit_logs(
        df,
        search_text,
        selected_agent,
        selected_status,
        start_date,
        end_date
    )

    st.caption(
        f"Showing {len(filtered_df)} of {len(df)} audit records"
    )

    st.divider()

    # -----------------------------------------
    # METRICS
    # -----------------------------------------

    render_execution_metrics(filtered_df)

    st.divider()

    # -----------------------------------------
    # AGENT PERFORMANCE
    # -----------------------------------------

    render_agent_performance(filtered_df)

    st.divider()

    # -----------------------------------------
    # FAILURE ANALYSIS
    # -----------------------------------------

    render_failure_analysis(filtered_df)

    st.divider()

    # -----------------------------------------
    # CASE TIMELINE
    # -----------------------------------------

    render_case_timeline(filtered_df)

    st.divider()

    # -----------------------------------------
    # COMPLETE AUDIT RECORDS
    # -----------------------------------------

    st.subheader("📋 Filtered Audit Records")

    st.dataframe(
        filtered_df.sort_values(
            "created_at",
            ascending=False,
            na_position="last"
        ),
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------
    # CSV EXPORT
    # -----------------------------------------

    render_audit_export(filtered_df)
