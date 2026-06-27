VALID_TRANSITIONS = {
    'grievance': {
        'pending': ['in_progress', 'resolved', 'rejected'],
        'in_progress': ['resolved', 'rejected'],
        'resolved': [],
        'rejected': [],
    },
    'appointment': {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': [],
    },
}


def is_valid_transition(ticket_type, current_status, new_status):
    allowed_map = VALID_TRANSITIONS.get(ticket_type)
    if allowed_map is None:
        return False, f"Unknown ticket type: {ticket_type}"

    allowed_next = allowed_map.get(current_status)
    if allowed_next is None:
        return False, f"Unknown current status: {current_status}"

    if new_status not in allowed_next:
        return False, (
            f"Invalid transition: cannot move '{ticket_type}' from "
            f"'{current_status}' to '{new_status}'."
        )

    return True, None