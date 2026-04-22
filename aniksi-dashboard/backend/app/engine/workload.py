from app.config import settings
from app.models.agent import AlertState


def workload_score(
    active_chats_estimated: int,
    assigned_open_tickets: int,
    overdue_assigned_tickets: int,
) -> float:
    return (
        active_chats_estimated * 10
        + assigned_open_tickets * 2.5
        + overdue_assigned_tickets * 4
    )


def agent_alert_state(utilization: float) -> AlertState:
    s = settings
    if utilization > s.util_warning_ceil:
        return AlertState.overloaded
    if utilization > s.util_healthy_ceil:
        return AlertState.warning
    if utilization < s.util_healthy_floor:
        return AlertState.ok
    return AlertState.ok


def agent_recommendation(
    utilization: float,
    active_chats: int,
    open_tickets: int,
    current_role: str,
    chat_pressure: float,
    ticket_pressure: float,
) -> str:
    s = settings
    if utilization > s.util_warning_ceil:
        return "overloaded"
    if utilization < s.util_healthy_floor:
        if chat_pressure >= s.pressure_amber and current_role != "chat_core":
            return "help_chat"
        if ticket_pressure >= s.pressure_amber and current_role != "ticket_core":
            return "help_ticket"
        return "take_break"
    return "stay"
