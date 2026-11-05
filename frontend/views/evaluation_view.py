import streamlit as st
import pandas as pd
import plotly.express as px

from time import perf_counter
from frontend.api_client import api_get
from evaluation.evaluator import evaluate_response


def render_evaluation_view():

    st.title("📊 AI Response Evaluation")

    st.caption(
        "Monitor RAG quality, response accuracy indicators "
        "and historical evaluation performance."
    )

    # =====================================
    # SECTION 1 - EVALUATION SUMMARY
    # =====================================

    st.header("Evaluation Performance")

    try:

        summary_response = api_get(
            "/api/evaluation/summary",
            timeout=10
        )

        summary_response.raise_for_status()

        summary = summary_response.json()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Evaluations",
            summary.get("total_evaluations", 0)
        )

        col2.metric(
            "Answer Relevance",
            f"{summary.get('average_answer_relevance', 0):.4f}"
        )

        col3.metric(
            "Faithfulness",
            f"{summary.get('average_faithfulness', 0):.4f}"
        )

        col4, col5, col6 = st.columns(3)

        col4.metric(
            "Context Precision",
            f"{summary.get('average_context_precision', 0):.4f}"
        )

        col5.metric(
            "Context Recall",
            f"{summary.get('average_context_recall', 0):.4f}"
        )

        col6.metric(
            "Overall Score",
            f"{summary.get('average_overall_score', 0):.4f}"
        )

        st.metric(
            "Average Response Time",
            f"{summary.get('average_response_time', 0):.2f} sec"
        )

    except Exception as error:

        st.error(
            f"Evaluation Summary API Error: {error}"
        )

    # =====================================
    # SECTION 2 - MANUAL EVALUATION
    # =====================================

    st.divider()

    st.header("Manual Response Evaluation")

    question = st.text_input(
        "Customer Question",
        value="What is the refund policy?"
    )

    answer = st.text_area(
        "Generated Answer",
        value=(
            "Customers can request a refund "
            "according to applicable refund conditions."
        )
    )

    context = st.text_area(
        "Retrieved Policy Context",
        value=(
            "Customers can request a refund "
            "according to applicable refund conditions."
        )
    )

    if st.button("Evaluate Response"):

        if not question.strip() or not answer.strip() or not context.strip():

            st.warning("Please enter all evaluation fields.")

        else:

            start_time = perf_counter()

            metrics = evaluate_response(
                customer_question=question,
                generated_answer=answer,
                policy_context=context,
                retrieved_contexts=[context],
                relevant_keywords=["refund"],
                expected_keywords=["refund", "conditions"],
                start_time=start_time
            )

            st.subheader("Manual Evaluation Results")

            col1, col2 = st.columns(2)

            col1.metric(
                "Answer Relevance",
                f"{metrics['answer_relevance']:.4f}"
            )

            col2.metric(
                "Faithfulness",
                f"{metrics['faithfulness']:.4f}"
            )

            col3, col4 = st.columns(2)

            col3.metric(
                "Context Precision",
                f"{metrics['context_precision']:.4f}"
            )

            col4.metric(
                "Context Recall",
                f"{metrics['context_recall']:.4f}"
            )

            col5, col6 = st.columns(2)

            col5.metric(
                "Overall Score",
                f"{metrics['overall_score']:.4f}"
            )

            col6.metric(
                "Evaluation Time",
                f"{metrics['response_time_seconds']:.4f} sec"
            )

            st.info(
                "Manual evaluation is calculated locally. "
                "It is not saved to database history."
            )

    # =====================================
    # SECTION 3 - EVALUATION HISTORY
    # =====================================

    st.divider()

    st.header("Evaluation History")

    try:

        history_response = api_get(
            "/api/evaluation/history",
            timeout=10
        )

        history_response.raise_for_status()

        history = history_response.json()

        if history:

            df = pd.DataFrame(history)

            display_columns = [
                "case_id",
                "ticket_id",
                "customer_question",
                "answer_relevance",
                "faithfulness",
                "context_precision",
                "context_recall",
                "overall_score",
                "response_time_seconds",
                "created_at"
            ]

            df = df[
                [
                    column
                    for column in display_columns
                    if column in df.columns
                ]
            ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # =====================================
            # SECTION 4 - PERFORMANCE CHARTS
            # =====================================

            st.divider()

            st.header("Evaluation Performance Charts")

            chart_df = pd.DataFrame(history)

            if "created_at" in chart_df.columns:

                chart_df["created_at"] = pd.to_datetime(
                    chart_df["created_at"],
                    errors="coerce"
                )

                chart_df = chart_df.dropna(
                    subset=["created_at"]
                ).sort_values("created_at")

            if not chart_df.empty:

                metric_options = [
                    "answer_relevance",
                    "faithfulness",
                    "context_precision",
                    "context_recall",
                    "overall_score"
                ]

                selected_metric = st.selectbox(
                    "Select Evaluation Metric",
                    metric_options
                )

                if selected_metric in chart_df.columns:

                    fig = px.line(
                        chart_df,
                        x="created_at",
                        y=selected_metric,
                        markers=True,
                        title=(
                            f"{selected_metric.replace('_', ' ').title()} Trend"
                        )
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                if (
                    "ticket_id" in chart_df.columns
                    and "response_time_seconds" in chart_df.columns
                ):

                    response_fig = px.bar(
                        chart_df,
                        x="ticket_id",
                        y="response_time_seconds",
                        title="Response Time by Ticket"
                    )

                    st.plotly_chart(
                        response_fig,
                        use_container_width=True
                    )

        else:

            st.info(
                "No evaluation history available. "
                "Submit a customer message through Customer Chat first."
            )

    except Exception as error:

        st.error(
            f"Evaluation History API Error: {error}"
        )