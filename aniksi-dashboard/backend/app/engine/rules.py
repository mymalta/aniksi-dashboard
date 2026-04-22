from dataclasses import dataclass
from app.config import settings
from app.schemas.dashboard import Recommendation


@dataclass
class EngineInputs:
    queued_chats: int
    avg_chat_wait_15m: float
    chats_per_chat_core_agent: float
    chat_pressure: float
    unassigned_open_tickets: int
    overdue_tickets: int
    ticket_pressure: float
    flex_agents: list[dict]           # list of {agent_id, agent_name, utilization_score}
    overloaded_mixed_agents: list[dict]  # agents triggering Rule C


def _rule_a_score(inputs: EngineInputs) -> int:
    """Count how many Rule A triggers are active (fires on >= 2)."""
    s = settings
    hits = 0
    if inputs.queued_chats >= s.rule_a_queued_chats:
        hits += 1
    if inputs.avg_chat_wait_15m >= s.rule_a_wait_time:
        hits += 1
    if inputs.chats_per_chat_core_agent >= s.rule_a_chats_per_agent:
        hits += 1
    if inputs.chat_pressure >= s.rule_a_chat_pressure:
        hits += 1
    return hits


def _best_flex(agents: list[dict]) -> dict | None:
    available = [a for a in agents if a.get("current_role") == "flex"]
    if not available:
        return None
    return min(available, key=lambda a: a["utilization_score"])


def evaluate(inputs: EngineInputs) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    s = settings

    # Rule A: move Flex to chats
    if _rule_a_score(inputs) >= 2:
        agent = _best_flex(inputs.flex_agents)
        if agent:
            confidence = min(1.0, _rule_a_score(inputs) / 4)
            reasons = []
            if inputs.queued_chats >= s.rule_a_queued_chats:
                reasons.append(f"queued chats={inputs.queued_chats}")
            if inputs.avg_chat_wait_15m >= s.rule_a_wait_time:
                reasons.append(f"avg wait={inputs.avg_chat_wait_15m:.0f}s")
            if inputs.chats_per_chat_core_agent >= s.rule_a_chats_per_agent:
                reasons.append(f"chats/agent={inputs.chats_per_chat_core_agent:.1f}")
            recommendations.append(Recommendation(
                action="move_flex_to_chat",
                agent_id=agent["agent_id"],
                agent_name=agent["agent_name"],
                from_role="flex",
                to_role="chat_core",
                confidence=confidence,
                reason=", ".join(reasons),
            ))
        return recommendations

    # Rule B: move Flex to tickets (all conditions must be true)
    rule_b = (
        inputs.queued_chats <= s.rule_b_queued_chats_max
        and inputs.avg_chat_wait_15m < s.rule_b_wait_time_max
        and (
            inputs.unassigned_open_tickets >= s.rule_b_unassigned_tickets
            or inputs.overdue_tickets >= s.rule_b_overdue_tickets
        )
        and inputs.ticket_pressure >= s.rule_b_ticket_pressure
    )
    if rule_b:
        agent = _best_flex(inputs.flex_agents)
        if agent:
            reasons = []
            if inputs.unassigned_open_tickets >= s.rule_b_unassigned_tickets:
                reasons.append(f"unassigned tickets={inputs.unassigned_open_tickets}")
            if inputs.overdue_tickets >= s.rule_b_overdue_tickets:
                reasons.append(f"overdue tickets={inputs.overdue_tickets}")
            recommendations.append(Recommendation(
                action="move_flex_to_ticket",
                agent_id=agent["agent_id"],
                agent_name=agent["agent_name"],
                from_role="flex",
                to_role="ticket_core",
                confidence=0.75,
                reason=", ".join(reasons),
            ))

    # Rule C: protect overloaded mixed-role agents
    for agent in inputs.overloaded_mixed_agents:
        recommendations.append(Recommendation(
            action="protect_from_ticket_intake",
            agent_id=agent["agent_id"],
            agent_name=agent["agent_name"],
            from_role=agent["current_role"],
            to_role=agent["current_role"],
            confidence=0.95,
            reason=f"utilization {agent['utilization_score']:.0%} for 30+ min, mixed chat+ticket load",
        ))

    return recommendations
