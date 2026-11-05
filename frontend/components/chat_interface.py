
import streamlit as st

from datetime import datetime

from frontend.api_client import api_get, api_post


# -----------------------------------------
# INITIALIZE CHAT SESSION
# -----------------------------------------

def initialize_chat_state():

    defaults = {
        "messages": [],
        "case_id": None,
        "ticket_id": None,
        "conversation_pending": False,
        "history_loaded": False
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# -----------------------------------------
# EVALUATION METRICS
# -----------------------------------------

def render_evaluation(evaluation):

    if not evaluation:
        return

    with st.expander("📊 Evaluation Metrics"):

        col1, col2 = st.columns(2)

        col1.metric(
            "Answer Relevance",
            f"{evaluation.get('answer_relevance') or 0:.4f}"
        )

        col2.metric(
            "Faithfulness",
            f"{evaluation.get('faithfulness') or 0:.4f}"
        )

        col3, col4 = st.columns(2)

        col3.metric(
            "Context Precision",
            f"{evaluation.get('context_precision') or 0:.4f}"
        )

        col4.metric(
            "Response Time",
            f"{evaluation.get('response_time_seconds') or 0:.2f} sec"
        )


# -----------------------------------------
# LOAD ALL CONVERSATIONS
# -----------------------------------------

def load_conversations():

    try:

        response = api_get(
            "/api/conversations",
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data if isinstance(data, list) else []

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
            f"Unable to load conversations: {error_message}"
        )

        return []


# -----------------------------------------
# LOAD SELECTED CONVERSATION HISTORY
# -----------------------------------------

def load_conversation_history(case_id, ticket_id):

    try:

        response = api_get(
            f"/api/conversations/{case_id}/{ticket_id}",
            timeout=30
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
            f"Unable to load conversation history: {error_message}"
        )

        return None


# -----------------------------------------
# RESTORE CONVERSATION
# -----------------------------------------

def restore_conversation(case_id, ticket_id):

    history = load_conversation_history(
        case_id,
        ticket_id
    )

    if not history:
        return False

    restored_messages = []

    for message in history.get("messages", []):

        restored_messages.append({
            "role": message["role"],
            "content": message["content"],
            "evaluation": message.get("evaluation")
        })

    st.session_state.messages = restored_messages

    st.session_state.case_id = history.get("case_id")

    st.session_state.ticket_id = history.get("ticket_id")

    st.session_state.conversation_pending = (
        history.get("status") == "awaiting_order_id"
    )

    st.session_state.history_loaded = True

    return True


# -----------------------------------------
# SEARCH CONVERSATIONS
# -----------------------------------------

def search_conversations(conversations, search_text):

    if not search_text:
        return conversations

    search_text = search_text.strip().lower()

    filtered_conversations = []

    for item in conversations:

        searchable_text = " ".join([
            str(item.get("case_id") or ""),
            str(item.get("ticket_id") or ""),
            str(item.get("order_id") or ""),
            str(item.get("last_message") or ""),
            str(item.get("customer_message") or ""),
            str(item.get("status") or ""),
            str(item.get("created_at") or "")
        ]).lower()

        if search_text in searchable_text:

            filtered_conversations.append(item)

    return filtered_conversations


# -----------------------------------------
# CONVERSATION LABEL
# -----------------------------------------

def get_conversation_label(item):

    ticket_id = item.get("ticket_id") or "No Ticket"

    order_id = item.get("order_id") or "Order pending"

    last_message = (
        item.get("last_message")
        or item.get("customer_message")
        or "No message"
    )

    last_message = str(last_message).replace("\n", " ")

    if len(last_message) > 45:
        last_message = last_message[:45] + "..."

    return f"{ticket_id} | {order_id} | {last_message}"


# -----------------------------------------
# DISPLAY MESSAGE HISTORY
# -----------------------------------------

def render_message_history():

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])

            if message.get("evaluation"):

                render_evaluation(
                    message["evaluation"]
                )

            if message.get("case_details"):

                with st.expander("Case Details"):

                    details = message["case_details"]

                    st.write("Case ID:", details.get("case_id"))
                    st.write("Ticket ID:", details.get("ticket_id"))
                    st.write("Intent:", details.get("intent"))
                    st.write("Order ID:", details.get("order_id"))
                    st.write("Priority:", details.get("priority"))


# -----------------------------------------
# GENERATE CONVERSATION EXPORT
# -----------------------------------------

def generate_conversation_export():

    lines = []

    lines.append("CUSTOMER SUPPORT CONVERSATION")
    lines.append("=" * 60)

    lines.append(
        f"Case ID: {st.session_state.case_id or 'Not available'}"
    )

    lines.append(
        f"Ticket ID: {st.session_state.ticket_id or 'Not available'}"
    )

    lines.append(
        f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    lines.append("=" * 60)

    for message in st.session_state.messages:

        role = message.get("role", "unknown").upper()

        content = message.get("content", "")

        lines.append("")
        lines.append("-" * 60)
        lines.append(role)
        lines.append("-" * 60)

        lines.append(str(content))

        evaluation = message.get("evaluation")

        if evaluation:

            lines.append("")
            lines.append("EVALUATION METRICS")

            metric_names = {
                "answer_relevance": "Answer Relevance",
                "faithfulness": "Faithfulness",
                "context_precision": "Context Precision",
                "context_recall": "Context Recall",
                "overall_score": "Overall Score",
                "response_time_seconds": "Response Time"
            }

            for key, label in metric_names.items():

                value = evaluation.get(key)

                if value is not None:

                    lines.append(f"{label}: {value}")

        case_details = message.get("case_details")

        if case_details:

            lines.append("")
            lines.append("CASE DETAILS")

            for key, value in case_details.items():

                lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF CONVERSATION")

    return "\n".join(lines)


# -----------------------------------------
# DOWNLOAD CONVERSATION
# -----------------------------------------

def render_conversation_download():

    if not st.session_state.messages:
        return

    export_content = generate_conversation_export()

    ticket_id = (
        st.session_state.ticket_id
        or "new_conversation"
    )

    st.download_button(
        label="📥 Download Conversation",
        data=export_content,
        file_name=f"{ticket_id}_conversation.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_conversation"
    )


# -----------------------------------------
# SIDEBAR - CONVERSATION SEARCH & FILTER
# -----------------------------------------

def render_conversation_sidebar():

    with st.sidebar:

        st.subheader("🗂️ Previous Conversations")

        conversations = load_conversations()

        if not conversations:

            st.info("No previous conversations available.")

            return

        search_text = st.text_input(
            "🔍 Search Conversations",
            placeholder="Search Ticket ID, Case ID, Order ID or message...",
            key="conversation_search"
        )

        filtered_conversations = search_conversations(
            conversations,
            search_text
        )

        st.caption(
            f"Showing {len(filtered_conversations)} of {len(conversations)} conversations"
        )

        if not filtered_conversations:

            st.warning("No matching conversations found.")

            return

        options = {}

        for index, item in enumerate(filtered_conversations):

            label = get_conversation_label(item)

            unique_label = f"{label} ({index + 1})"

            options[unique_label] = item

        selected = st.selectbox(
            "Select a conversation",
            ["Current Conversation"] + list(options.keys()),
            key="selected_conversation"
        )

        if selected != "Current Conversation":

            selected_conversation = options[selected]

            st.divider()

            st.caption("Selected Conversation Details")

            st.write(
                "Ticket ID:",
                selected_conversation.get("ticket_id")
            )

            st.write(
                "Case ID:",
                selected_conversation.get("case_id")
            )

            st.write(
                "Order ID:",
                selected_conversation.get("order_id") or "Pending"
            )

            if st.button(
                "📂 Load Conversation",
                use_container_width=True
            ):

                success = restore_conversation(
                    selected_conversation["case_id"],
                    selected_conversation["ticket_id"]
                )

                if success:

                    st.query_params["case_id"] = (
                        selected_conversation["case_id"]
                    )

                    st.query_params["ticket_id"] = (
                        selected_conversation["ticket_id"]
                    )

                    st.rerun()


# -----------------------------------------
# MAIN CHAT INTERFACE
# -----------------------------------------

def render_chat_interface():

    initialize_chat_state()

    st.subheader("💬 Customer Support Chat")

    # RESTORE CHAT AFTER REFRESH

    query_case_id = st.query_params.get("case_id")

    query_ticket_id = st.query_params.get("ticket_id")

    if (
        query_case_id
        and query_ticket_id
        and not st.session_state.history_loaded
    ):

        restore_conversation(
            query_case_id,
            query_ticket_id
        )

    # SIDEBAR

    render_conversation_sidebar()

    # DISPLAY CHAT HISTORY

    render_message_history()

    # DOWNLOAD CONVERSATION

    render_conversation_download()

    # CUSTOMER INPUT

    user_message = st.chat_input(
        "Describe your issue or provide your Order ID..."
    )

    if user_message:

        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):

            st.write(user_message)

        with st.chat_message("assistant"):

            with st.spinner("AI agents are processing..."):

                try:

                    payload = {
                        "message": user_message,
                        "case_id": st.session_state.case_id,
                        "ticket_id": st.session_state.ticket_id
                    }

                    response = api_post(
                        "/api/chat",
                        json=payload,
                        timeout=180
                    )

                    response.raise_for_status()

                    result = response.json()

                    answer = result.get(
                        "final_response",
                        "No response received."
                    )

                    # SAVE CONVERSATION IDs

                    st.session_state.case_id = result.get("case_id")

                    st.session_state.ticket_id = result.get("ticket_id")

                    st.session_state.conversation_pending = (
                        result.get("awaiting_order_id", False)
                    )

                    # SAVE IDs IN URL

                    if st.session_state.case_id:

                        st.query_params["case_id"] = (
                            st.session_state.case_id
                        )

                    if st.session_state.ticket_id:

                        st.query_params["ticket_id"] = (
                            st.session_state.ticket_id
                        )

                    st.write(answer)

                    # CASE DETAILS

                    case_details = {
                        "case_id": result.get("case_id"),
                        "ticket_id": result.get("ticket_id"),
                        "intent": result.get("intent"),
                        "order_id": result.get("order_id"),
                        "priority": result.get("priority")
                    }

                    with st.expander("Case Details"):

                        st.write("Case ID:", case_details["case_id"])
                        st.write("Ticket ID:", case_details["ticket_id"])
                        st.write("Intent:", case_details["intent"])
                        st.write("Order ID:", case_details["order_id"])
                        st.write("Priority:", case_details["priority"])

                    # EVALUATION

                    evaluation = result.get("evaluation") or {}

                    if evaluation:

                        render_evaluation(evaluation)

                    else:

                        st.info(
                            "Evaluation results are not available."
                        )

                    # SAVE ASSISTANT RESPONSE

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "evaluation": evaluation,
                        "case_details": case_details
                    })

                    st.session_state.history_loaded = True

                    st.rerun()

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

                    answer = f"Request failed: {error_message}"

                    st.error(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "evaluation": None
                    })

    # START NEW CONVERSATION

    if st.session_state.messages:

        if st.button("➕ Start New Conversation"):

            st.session_state.messages = []

            st.session_state.case_id = None

            st.session_state.ticket_id = None

            st.session_state.conversation_pending = False

            st.session_state.history_loaded = False

            st.session_state.pop(
                "conversation_search",
                None
            )

            st.session_state.pop(
                "selected_conversation",
                None
            )

            st.query_params.clear()

            st.rerun()
