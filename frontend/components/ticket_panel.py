
import streamlit as st

from frontend.api_client import api_put


TICKET_STATUSES = [
    "open",
    "awaiting_order_id",
    "in_progress",
    "resolved",
    "escalated"
]

TICKET_PRIORITIES = [
    "low",
    "normal",
    "high",
    "critical"
]


# -----------------------------------------
# SEARCH TICKETS
# -----------------------------------------

def search_tickets(tickets, search_text):

    if not search_text:
        return tickets

    search_text = search_text.strip().lower()

    filtered = []

    for ticket in tickets:

        searchable_text = " ".join([
            str(ticket.get("ticket_id") or ""),
            str(ticket.get("customer_id") or ""),
            str(ticket.get("order_id") or ""),
            str(ticket.get("intent") or ""),
            str(ticket.get("customer_message") or ""),
            str(ticket.get("status") or ""),
            str(ticket.get("priority") or "")
        ]).lower()

        if search_text in searchable_text:
            filtered.append(ticket)

    return filtered


# -----------------------------------------
# UPDATE TICKET
# -----------------------------------------

def update_ticket(ticket_id, status, priority):

    try:

        response = api_put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": status,
                "priority": priority
            },
            timeout=15
        )

        response.raise_for_status()

        return True, "Ticket updated successfully!"

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
# TICKET STATUS SUMMARY
# -----------------------------------------

def render_ticket_summary(tickets):

    total = len(tickets)

    resolved = sum(
        1 for ticket in tickets
        if ticket.get("status") == "resolved"
    )

    escalated = sum(
        1 for ticket in tickets
        if ticket.get("status") == "escalated"
    )

    pending = sum(
        1 for ticket in tickets
        if ticket.get("status") in [
            "open",
            "pending",
            "in_progress",
            "awaiting_order_id"
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tickets", total)
    col2.metric("Resolved", resolved)
    col3.metric("Pending", pending)
    col4.metric("Escalated", escalated)


# -----------------------------------------
# MAIN TICKET PANEL
# -----------------------------------------

def render_ticket_panel(tickets=None):

    st.subheader("🎫 Ticket Management")

    if tickets is None:
        st.error("Ticket data is not available.")
        return

    if not tickets:
        st.info("No tickets available yet.")
        return

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------

    render_ticket_summary(tickets)

    st.divider()

    # -----------------------------------------
    # SEARCH
    # -----------------------------------------

    st.subheader("🔍 Search & Filter Tickets")

    search_text = st.text_input(
        "Search Ticket",
        placeholder="Ticket ID, Order ID, Customer ID or message...",
        key="ticket_search"
    )

    col1, col2 = st.columns(2)

    with col1:

        status_filter = st.selectbox(
            "Filter by Status",
            [
                "All",
                "open",
                "awaiting_order_id",
                "in_progress",
                "resolved",
                "escalated"
            ],
            key="ticket_status_filter"
        )

    with col2:

        priority_filter = st.selectbox(
            "Filter by Priority",
            [
                "All",
                "low",
                "normal",
                "high",
                "critical"
            ],
            key="ticket_priority_filter"
        )

    # -----------------------------------------
    # APPLY FILTERS
    # -----------------------------------------

    filtered_tickets = search_tickets(
        tickets,
        search_text
    )

    if status_filter != "All":

        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if ticket.get("status") == status_filter
        ]

    if priority_filter != "All":

        filtered_tickets = [
            ticket for ticket in filtered_tickets
            if ticket.get("priority") == priority_filter
        ]

    st.caption(
        f"Showing {len(filtered_tickets)} of {len(tickets)} tickets"
    )

    if not filtered_tickets:

        st.warning("No matching tickets found.")
        return

    st.divider()

    # -----------------------------------------
    # DISPLAY TICKETS
    # -----------------------------------------

    for ticket in filtered_tickets:

        ticket_id = ticket.get("ticket_id")

        if not ticket_id:
            continue

        current_status = ticket.get("status", "open")

        current_priority = ticket.get("priority", "normal")

        if current_status not in TICKET_STATUSES:
            current_status = "open"

        if current_priority not in TICKET_PRIORITIES:
            current_priority = "normal"

        with st.container(border=True):

            st.markdown(f"### 🎫 {ticket_id}")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Customer ID:**",
                    ticket.get("customer_id")
                )

                st.write(
                    "**Order ID:**",
                    ticket.get("order_id") or "Not available"
                )

                st.write(
                    "**Intent:**",
                    ticket.get("intent") or "Not available"
                )

            with col2:

                st.write(
                    "**Priority:**",
                    current_priority.upper()
                )

                st.write(
                    "**Current Status:**",
                    current_status.upper()
                )

            st.write("**Customer Message:**")

            st.write(
                ticket.get("customer_message")
                or "No message available."
            )

            if ticket.get("escalation_reason"):

                st.warning(
                    f"Escalation: {ticket['escalation_reason']}"
                )

            st.divider()

            # ---------------------------------
            # UPDATE STATUS
            # ---------------------------------

            st.markdown("#### ⚙️ Update Ticket")

            col1, col2 = st.columns(2)

            with col1:

                new_status = st.selectbox(
                    "Ticket Status",
                    TICKET_STATUSES,
                    index=TICKET_STATUSES.index(current_status),
                    key=f"status_{ticket_id}"
                )

            with col2:

                new_priority = st.selectbox(
                    "Ticket Priority",
                    TICKET_PRIORITIES,
                    index=TICKET_PRIORITIES.index(current_priority),
                    key=f"priority_{ticket_id}"
                )

            if st.button(
                "💾 Save Ticket Changes",
                key=f"update_{ticket_id}",
                use_container_width=True
            ):

                success, message = update_ticket(
                    ticket_id,
                    new_status,
                    new_priority
                )

                if success:

                    st.success(message)
                    st.rerun()

                else:

                    st.error(
                        f"Ticket update failed: {message}"
                    )
