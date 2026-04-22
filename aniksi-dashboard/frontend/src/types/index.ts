export type PressureStatus = "green" | "amber" | "red";
export type AlertState = "ok" | "warning" | "critical" | "overloaded";
export type PlannedRole = "chat_core" | "ticket_core" | "flex" | "off";
export type AgentRecommendation = "stay" | "help_chat" | "help_ticket" | "take_break" | "overloaded";

export interface Recommendation {
  action: string;
  agent_id: string;
  agent_name: string;
  from_role: string;
  to_role: string;
  confidence: number;
  reason: string;
}

export interface LiveOverview {
  generated_at: string;
  scheduled_agents: number;
  online_agents: number;
  agents_on_break: number;
  active_chats: number;
  queued_chats: number;
  open_tickets: number;
  unassigned_tickets: number;
  overdue_tickets: number;
  avg_chat_wait_seconds: number;
  chat_pressure: number;
  ticket_pressure: number;
  global_pressure: number;
  status: PressureStatus;
  recommendations: Recommendation[];
}

export interface LiveAgentState {
  agent_id: string;
  agent_name: string;
  scheduled: boolean;
  shift_start: string;
  shift_end: string;
  planned_role: PlannedRole;
  current_role: PlannedRole;
  presence_status: string;
  presence_stale: boolean;
  absence_seconds: number;
  active_chats_estimated: number;
  chats_unowned: boolean;
  assigned_open_tickets: number;
  overdue_assigned_tickets: number;
  workload_score: number;
  utilization_score: number;
  alert_state: AlertState;
  recommendation: AgentRecommendation;
}

export interface AgentBoardResponse {
  generated_at: string;
  agents: LiveAgentState[];
}
