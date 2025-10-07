ALLOWED = {
    "QUEUED": ["SENDING"],
    "SENDING": ["SENT", "FAILED", "UNDLVD"],
    "SENT": ["DELIVERED", "FAILED", "UNDLVD"],
    "DELIVERED": ["READ"],
    "READ": [],
    "FAILED": [],
    "UNDLVD": []
}

def can_transition(current, new_state):
    if current == new_state:
        return True
    return new_state in ALLOWED.get(current, [])
