from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://aniksi:aniksi@localhost:5432/aniksi_dashboard"
    redis_url: str = "redis://localhost:6379"

    # Polling intervals (seconds)
    livechat_poll_interval: int = 30
    helpdesk_poll_interval: int = 120
    presence_poll_interval: int = 30
    schedule_poll_interval: int = 900
    engine_interval: int = 60

    # Absence thresholds (seconds)
    absence_grace_seconds: int = 300       # 5 min — do nothing
    absence_unowned_seconds: int = 900     # 15 min — coverage substitution

    # Normalisation ceilings (0.0 = floor, 1.0 = ceiling)
    norm_queued_chats_ceil: float = 12
    norm_wait_time_ceil: float = 180
    norm_chats_per_agent_floor: float = 2.0
    norm_chats_per_agent_ceil: float = 5.5
    norm_active_chats_ceil: float = 20
    norm_unassigned_tickets_ceil: float = 25
    norm_overdue_tickets_ceil: float = 15
    norm_avg_ticket_age_ceil: float = 10       # hours
    norm_new_tickets_60m_ceil: float = 20
    norm_tickets_per_agent_floor: float = 5
    norm_tickets_per_agent_ceil: float = 25

    # Pressure thresholds
    pressure_amber: float = 0.60
    pressure_red: float = 0.80

    # Utilisation thresholds
    util_healthy_floor: float = 0.65
    util_healthy_ceil: float = 0.80
    util_warning_ceil: float = 0.90

    # Role-switch rule A triggers
    rule_a_queued_chats: int = 6
    rule_a_wait_time: float = 90
    rule_a_chats_per_agent: float = 4.5
    rule_a_chat_pressure: float = 0.80

    # Role-switch rule B triggers
    rule_b_queued_chats_max: int = 2
    rule_b_wait_time_max: float = 45
    rule_b_unassigned_tickets: int = 12
    rule_b_overdue_tickets: int = 8
    rule_b_ticket_pressure: float = 0.70

    # Rule C triggers
    rule_c_util_threshold: float = 0.90
    rule_c_util_duration_seconds: int = 1800   # 30 min
    rule_c_active_chats_min: int = 2
    rule_c_open_tickets_min: int = 8

    # Escalation
    escalation_red_duration_seconds: int = 1800  # 30 min

    # Alert cooldowns (seconds)
    alert_cooldown_chat_overload: int = 600
    alert_cooldown_ticket_backlog: int = 600
    alert_cooldown_agent_overload: int = 900
    alert_cooldown_coverage_gap: int = 300

    class Config:
        env_file = ".env"


settings = Settings()
