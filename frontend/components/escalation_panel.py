
import streamlit as st

from frontend.api_client import api_put


ESCALATION_STATUSES = [
    "escalated",
    "in_progress",
    "resolved"
]

PRIORITIES = [
    "All",
    "low",
    "normal",
    "high",
    "critical",
    "urgent"
]


# -----------------------------------------
# SEARCH ESCALATIONS
# -----------------------------------------

def search_escalations(escalations, search_text):

    if not search_text:
        return escalations

    search_text = search_text.strip().lower()

    filtered = []

    for item in escalations:

        searchable_text = " ".join([
            str(item.get("case_id") or ""),
            str(item.get("ticket_id") or ""),
            str(item.get("order_id") or ""),
            str(item.get("customer_id") or ""),
            str(item.get("customer_message") or ""),
            str(item.get("escalation_reason") or ""),
            str(item.get("priority") or "")
        ]).lower()

        if search_text in searchable_text:
            filtered.append(item)

    return filtered


# -----------------------------------------
# UPDATE ESCALATION STATUS
# -----------------------------------------

def update_escalation_status(ticket_id, status):

    try:

        response = api_put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": status
            },
            timeout=15
        )

        response.raise_for_status()

        return True, "Escalation status updated successfully!"

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

        return False, error_message


# -----------------------------------------
# ESCALATION SUMMARY
# -----------------------------------------

def render_escalation_summary(escalations):

    total = len(escalations)

    urgent = sum(
        1 for item in escalations
        if str(item.get("priority", "")).lower() == "urgent"
    )

    high = sum(
        1 for item in escalations
        if str(item.get("priority", "")).lower() == "high"
    )

    normal = sum(
        1 for item in escalations
        if str(item.get("priority", "")).lower()
        in ["normal", "low"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Escalations", total)
    col2.metric("Urgent", urgent)
    col3.metric("High Priority", high)
    col4.metric("Normal / Low", normal)


# -----------------------------------------
# PRIORITY DISPLAY
# -----------------------------------------

def render_priority(priority):

    priority = str(priority or "normal").lower()

    if priority in ["urgent", "critical"]:

        st.error(f"🚨 Priority: {priority.upper()}")

    elif priority == "high":

        st.warning(f"⚠️ Priority: {priority.upper()}")

    else:

        st.info(f"Priority: {priority.upper()}")


# -----------------------------------------
# MAIN ESCALATION PANEL
# -----------------------------------------

def render_escalation_panel(escalations=None):

    st.subheader("🚨 Human Support Escalation")

    if escalations is None:

        st.error("Unable to load escalation data.")
        return

    if not escalations:

        st.success("No pending escalations.")
        return

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------

    render_escalation_summary(escalations)

    st.divider()

    # -----------------------------------------
    # SEARCH
    # -----------------------------------------

    st.subheader("🔍 Search & Filter Escalations")

    search_text = st.text_input(
        "Search Escalations",
        placeholder="Ticket ID, Order ID, Customer ID or reason...",
        key="escalation_search"
    )

    priority_filter = st.selectbox(
        "Filter by Priority",
        PRIORITIES,
        key="escalation_priority_filter"
    )

    # -----------------------------------------
    # APPLY FILTERS
    # -----------------------------------------

    filtered_escalations = search_escalations(
        escalations,
        search_text
    )

    if priority_filter != "All":

        filtered_escalations = [
            item for item in filtered_escalations
            if str(item.get("priority", "")).lower()
            == priority_filter.lower()
        ]

    st.caption(
        f"Showing {len(filtered_escalations)} of {len(escalations)} escalations"
    )

    if not filtered_escalations:

        st.warning("No matching escalations found.")
        return

    st.divider()

    # -----------------------------------------
    # DISPLAY ESCALATIONS
    # -----------------------------------------

    for item in filtered_escalations:

        ticket_id = item.get("ticket_id")

        with st.container(border=True):

            st.markdown(
                f"### 🚨 {ticket_id or 'Escalation'}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Case ID:**",
                    item.get("case_id", "Not available")
                )

                st.write(
                    "**Ticket ID:**",
                    ticket_id or "Not available"
                )

                st.write(
                    "**Customer ID:**",
                    item.get("customer_id", "Not available")
                )

            with col2:

                st.write(
                    "**Order ID:**",
                    item.get("order_id") or "Not available"
                )

                st.write(
                    "**Current Status:**",
                    str(item.get("status", "escalated")).upper()
                )

                st.write(
                    "**Queue:**",
                    item.get("queue", "human_support")
                )

            render_priority(
                item.get("priority")
            )

            st.write("**Customer Message:**")

            st.write(
                item.get("customer_message")
                or "No customer message available."
            )

            reason = (
                item.get("escalation_reason")
                or item.get("reason")
                or "Human review required."
            )

            st.warning(
                f"Escalation Reason: {reason}"
            )

            st.divider()

            # ---------------------------------
            # HUMAN REVIEW STATUS
            # ---------------------------------

            st.markdown("#### 👨‍💼 Human Review Management")

            if not ticket_id:

                st.warning(
                    "Ticket ID is unavailable. Status cannot be updated."
                )

                continue

            current_status = item.get(
                "status",
                "escalated"
            )

            if current_status not in ESCALATION_STATUSES:

                current_status = "escalated"

            new_status = st.selectbox(
                "Update Escalation Status",
                ESCALATION_STATUSES,
                index=ESCALATION_STATUSES.index(current_status),
                key=f"escalation_status_{ticket_id}"
            )

            if st.button(
                "💾 Update Escalation",
                key=f"save_escalation_{ticket_id}",
                use_container_width=True
            ):

                success, message = update_escalation_status(
                    ticket_id,
                    new_status
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(
                        f"Update failed: {message}"
                    )
