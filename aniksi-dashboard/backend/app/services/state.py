"""
Builds the live agent state and global dashboard state from DB + Redis.
Runs every engine_interval seconds via the background task.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.config import settings
from app.models.agent import AgentSchedule, PlannedRole, AlertState, RoleOverride
from app.models.chat import ChatEvent, ChatStatus
from app.models.ticket import TicketEvent, TicketStatus
from app.models.presence import PresenceEvent
from app.schemas.agent import LiveAgentState
from app.schemas.dashboard import LiveOverview, Recommendation
from app.engine import pressure as pressure_engine
from app.engine import workload as workload_engine
from app.engine.rules import EngineInputs, evaluate
from app.db.redis import redis_set, redis_get


PRESENCE_STALE_SECONDS = 180   # 3 min


async def _current_schedules(db: AsyncSession, now: datetime) -> list[AgentSchedule]:
    result = await db.execute(
        select(AgentSchedule).where(
            and_(
                AgentSchedule.shift_start <= now,
                AgentSchedule.shift_end >= now,
                AgentSchedule.planned_role != PlannedRole.off,
            )
        )
    )
    return list(result.scalars().all())


async def _latest_presence(db: AsyncSession, agent_id: str) -> PresenceEvent | None:
    result = await db.execute(
        select(PresenceEvent)
        .where(PresenceEvent.agent_id == agent_id)
        .order_by(PresenceEvent.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _active_role(db: AsyncSession, agent_id: str, now: datetime) -> PlannedRole | None:
    """Return active manual override role if one exists, else None."""
    result = await db.execute(
        select(RoleOverride).where(
            and_(
                RoleOverride.agent_id == agent_id,
                RoleOverride.active == True,
                (RoleOverride.expires_at == None) | (RoleOverride.expires_at >= now),
            )
        ).order_by(RoleOverride.created_at.desc()).limit(1)
    )
    override = result.scalar_one_or_none()
    return override.new_role if override else None


async def _agent_chats(db: AsyncSession, agent_id: str) -> int:
    result = await db.execute(
        select(func.count()).where(
            and_(
                ChatEvent.attributed_agent_id == agent_id,
                ChatEvent.status == ChatStatus.active,
            )
        )
    )
    return result.scalar_one() or 0


async def _agent_tickets(db: AsyncSession, agent_id: str, now: datetime) -> tuple[int, int]:
    """Returns (open_count, overdue_count)."""
    open_result = await db.execute(
        select(func.count()).where(
            and_(
                TicketEvent.assigned_agent_id == agent_id,
                TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending]),
            )
        )
    )
    overdue_result = await db.execute(
        select(func.count()).where(
            and_(
                TicketEvent.assigned_agent_id == agent_id,
                TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending]),
                TicketEvent.resolution_due_at != None,
                TicketEvent.resolution_due_at < now,
            )
        )
    )
    return open_result.scalar_one() or 0, overdue_result.scalar_one() or 0


async def build_agent_states(db: AsyncSession, now: datetime) -> list[LiveAgentState]:
    schedules = await _current_schedules(db, now)
    states: list[LiveAgentState] = []

    for sched in schedules:
        presence = await _latest_presence(db, sched.agent_id)
        override_role = await _active_role(db, sched.agent_id, now)
        current_role = override_role or sched.planned_role

        # Presence analysis
        if presence is None:
            presence_status = "unknown"
            presence_stale = True
            absence_seconds = 0
        else:
            age = (now - presence.recorded_at.replace(tzinfo=timezone.utc)).total_seconds()
            presence_stale = age > PRESENCE_STALE_SECONDS
            presence_status = "unknown" if presence_stale else presence.status
            is_offline = presence_status in ("offline", "away", "unknown")
            absence_seconds = int(age) if is_offline else 0

        chats_unowned = (
            settings.absence_grace_seconds
            <= absence_seconds
            < settings.absence_unowned_seconds
        )

        active_chats = await _agent_chats(db, sched.agent_id)
        open_tickets, overdue_tickets = await _agent_tickets(db, sched.agent_id, now)

        score = workload_engine.workload_score(active_chats, open_tickets, overdue_tickets)

        # Simple utilisation approximation: score / 100 as a proxy
        utilization = min(1.0, score / 100.0)

        alert = workload_engine.agent_alert_state(utilization)

        rec = workload_engine.agent_recommendation(
            utilization=utilization,
            active_chats=active_chats,
            open_tickets=open_tickets,
            current_role=current_role.value,
            chat_pressure=0.0,    # filled in by caller after global state is known
            ticket_pressure=0.0,
        )

        states.append(LiveAgentState(
            agent_id=sched.agent_id,
            agent_name=sched.agent_name,
            scheduled=True,
            shift_start=sched.shift_start,
            shift_end=sched.shift_end,
            planned_role=sched.planned_role,
            current_role=current_role,
            presence_status=presence_status,
            presence_stale=presence_stale,
            absence_seconds=absence_seconds,
            active_chats_estimated=active_chats,
            chats_unowned=chats_unowned,
            assigned_open_tickets=open_tickets,
            overdue_assigned_tickets=overdue_tickets,
            workload_score=score,
            utilization_score=utilization,
            alert_state=alert,
            recommendation=rec,
        ))

    return states


async def build_live_overview(db: AsyncSession, now: datetime) -> LiveOverview:
    agent_states = await build_agent_states(db, now)

    # Headcount
    scheduled = len(agent_states)
    online = sum(1 for a in agent_states if a.presence_status == "online")
    on_break = sum(1 for a in agent_states if a.presence_status == "break")

    chat_core_count = sum(1 for a in agent_states if a.current_role == PlannedRole.chat_core)
    ticket_core_count = sum(1 for a in agent_states if a.current_role == PlannedRole.ticket_core)

    # Live chat metrics
    active_chats_q = await db.execute(
        select(func.count()).where(ChatEvent.status == ChatStatus.active)
    )
    active_chats = active_chats_q.scalar_one() or 0

    queued_chats_q = await db.execute(
        select(func.count()).where(ChatEvent.status == ChatStatus.queued)
    )
    queued_chats = queued_chats_q.scalar_one() or 0

    avg_wait_q = await db.execute(
        select(func.avg(ChatEvent.wait_time_seconds)).where(
            and_(
                ChatEvent.status == ChatStatus.active,
                ChatEvent.assigned_at >= now - timedelta(minutes=15),
            )
        )
    )
    avg_wait = float(avg_wait_q.scalar_one() or 0)

    # Live ticket metrics
    open_tickets_q = await db.execute(
        select(func.count()).where(
            TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending])
        )
    )
    open_tickets = open_tickets_q.scalar_one() or 0

    unassigned_q = await db.execute(
        select(func.count()).where(
            and_(
                TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending]),
                TicketEvent.assigned_agent_id == None,
            )
        )
    )
    unassigned_tickets = unassigned_q.scalar_one() or 0

    overdue_q = await db.execute(
        select(func.count()).where(
            and_(
                TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending]),
                TicketEvent.resolution_due_at != None,
                TicketEvent.resolution_due_at < now,
            )
        )
    )
    overdue_tickets = overdue_q.scalar_one() or 0

    # Avg ticket age
    created_avg_q = await db.execute(
        select(func.avg(
            func.extract("epoch", now) - func.extract("epoch", TicketEvent.created_at)
        )).where(TicketEvent.status.in_([TicketStatus.open, TicketStatus.pending]))
    )
    avg_ticket_age_seconds = float(created_avg_q.scalar_one() or 0)
    avg_ticket_age_hours = avg_ticket_age_seconds / 3600

    new_tickets_60m_q = await db.execute(
        select(func.count()).where(
            TicketEvent.created_at >= now - timedelta(hours=1)
        )
    )
    new_tickets_60m = new_tickets_60m_q.scalar_one() or 0

    chats_per_chat_core = (active_chats / chat_core_count) if chat_core_count > 0 else 0
    tickets_per_ticket_core = (open_tickets / ticket_core_count) if ticket_core_count > 0 else 0

    cp = pressure_engine.chat_pressure(queued_chats, avg_wait, chats_per_chat_core, active_chats)
    tp = pressure_engine.ticket_pressure(
        unassigned_tickets, overdue_tickets, avg_ticket_age_hours, new_tickets_60m, tickets_per_ticket_core
    )
    gp = pressure_engine.global_pressure(cp, tp)
    status = pressure_engine.pressure_status(gp)

    # Build rule engine inputs
    flex_agents = [
        {
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "current_role": a.current_role.value,
            "utilization_score": a.utilization_score,
        }
        for a in agent_states
        if a.current_role == PlannedRole.flex
    ]

    overloaded_mixed = [
        {
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "current_role": a.current_role.value,
            "utilization_score": a.utilization_score,
        }
        for a in agent_states
        if (
            a.utilization_score > settings.rule_c_util_threshold
            and a.active_chats_estimated > settings.rule_c_active_chats_min
            and a.assigned_open_tickets > settings.rule_c_open_tickets_min
        )
    ]

    engine_inputs = EngineInputs(
        queued_chats=queued_chats,
        avg_chat_wait_15m=avg_wait,
        chats_per_chat_core_agent=chats_per_chat_core,
        chat_pressure=cp,
        unassigned_open_tickets=unassigned_tickets,
        overdue_tickets=overdue_tickets,
        ticket_pressure=tp,
        flex_agents=flex_agents,
        overloaded_mixed_agents=overloaded_mixed,
    )

    recommendations = evaluate(engine_inputs)

    overview = LiveOverview(
        generated_at=now,
        scheduled_agents=scheduled,
        online_agents=online,
        agents_on_break=on_break,
        active_chats=active_chats,
        queued_chats=queued_chats,
        open_tickets=open_tickets,
        unassigned_tickets=unassigned_tickets,
        overdue_tickets=overdue_tickets,
        avg_chat_wait_seconds=avg_wait,
        chat_pressure=round(cp, 3),
        ticket_pressure=round(tp, 3),
        global_pressure=round(gp, 3),
        status=status,
        recommendations=recommendations,
    )

    # Cache in Redis for WebSocket broadcasts
    await redis_set("dashboard:live", overview.model_dump(mode="json"), ex=120)

    return overview
