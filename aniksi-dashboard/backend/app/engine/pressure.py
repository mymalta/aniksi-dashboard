from app.config import settings


def _norm(value: float, floor: float, ceil: float) -> float:
    if ceil <= floor:
        return 0.0
    return min(1.0, max(0.0, (value - floor) / (ceil - floor)))


def chat_pressure(
    queued_chats: int,
    avg_wait_time_15m: float,
    chats_per_chat_core_agent: float,
    active_chats: int,
) -> float:
    s = settings
    return (
        0.35 * _norm(queued_chats, 0, s.norm_queued_chats_ceil)
        + 0.25 * _norm(avg_wait_time_15m, 0, s.norm_wait_time_ceil)
        + 0.25 * _norm(chats_per_chat_core_agent, s.norm_chats_per_agent_floor, s.norm_chats_per_agent_ceil)
        + 0.15 * _norm(active_chats, 0, s.norm_active_chats_ceil)
    )


def ticket_pressure(
    unassigned_open_tickets: int,
    overdue_tickets: int,
    avg_ticket_age_hours: float,
    new_tickets_last_60m: int,
    open_tickets_per_ticket_core_agent: float,
) -> float:
    s = settings
    return (
        0.30 * _norm(unassigned_open_tickets, 0, s.norm_unassigned_tickets_ceil)
        + 0.25 * _norm(overdue_tickets, 0, s.norm_overdue_tickets_ceil)
        + 0.20 * _norm(avg_ticket_age_hours, 0, s.norm_avg_ticket_age_ceil)
        + 0.15 * _norm(new_tickets_last_60m, 0, s.norm_new_tickets_60m_ceil)
        + 0.10 * _norm(open_tickets_per_ticket_core_agent, s.norm_tickets_per_agent_floor, s.norm_tickets_per_agent_ceil)
    )


def global_pressure(chat: float, ticket: float) -> float:
    return 0.55 * chat + 0.45 * ticket


def pressure_status(gp: float) -> str:
    if gp >= settings.pressure_red:
        return "red"
    if gp >= settings.pressure_amber:
        return "amber"
    return "green"
