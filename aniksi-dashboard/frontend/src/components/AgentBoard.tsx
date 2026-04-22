"use client";
import { useEffect, useState } from "react";
import { AgentBoardResponse, LiveAgentState, AlertState } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const roleLabel: Record<string, string> = {
  chat_core: "Chat",
  ticket_core: "Ticket",
  flex: "Flex",
  off: "Off",
};

const recLabel: Record<string, string> = {
  stay: "Stay",
  help_chat: "Help chats",
  help_ticket: "Help tickets",
  take_break: "Take break",
  overloaded: "Overloaded",
};

const recColor: Record<string, string> = {
  stay: "text-gray-400",
  help_chat: "text-blue-400",
  help_ticket: "text-blue-400",
  take_break: "text-gray-400",
  overloaded: "text-red-400 font-semibold",
};

function rowColor(alert: AlertState, utilization: number): string {
  if (alert === "overloaded") return "bg-red-900/40";
  if (alert === "warning") return "bg-amber-900/40";
  if (utilization < 0.45) return "bg-blue-900/20";
  return "";
}

function utilBar(u: number) {
  const pct = Math.round(u * 100);
  const color = u > 0.9 ? "bg-red-500" : u > 0.75 ? "bg-amber-400" : u < 0.45 ? "bg-blue-500" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 bg-gray-700 rounded-full h-1.5">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-300 w-8">{pct}%</span>
    </div>
  );
}

function presenceDot(status: string, stale: boolean) {
  const color = stale
    ? "bg-gray-500"
    : { online: "bg-green-400", away: "bg-amber-400", busy: "bg-amber-400", offline: "bg-gray-500", break: "bg-blue-400", unknown: "bg-gray-500" }[status] ?? "bg-gray-500";
  return <span className={`inline-block w-2 h-2 rounded-full ${color}`} title={stale ? "stale" : status} />;
}

export function AgentBoard() {
  const [data, setData] = useState<AgentBoardResponse | null>(null);

  useEffect(() => {
    function load() {
      fetch(`${API_URL}/dashboard/agents`)
        .then((r) => r.json())
        .then(setData)
        .catch(() => null);
    }
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  if (!data) return <p className="text-gray-500 text-sm">Loading agents...</p>;

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold text-white">Agent Workload</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="text-gray-400 border-b border-gray-700">
              <th className="pb-2 pr-4">Agent</th>
              <th className="pb-2 pr-4">Planned</th>
              <th className="pb-2 pr-4">Current</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2 pr-4">Chats</th>
              <th className="pb-2 pr-4">Tickets</th>
              <th className="pb-2 pr-4">Overdue</th>
              <th className="pb-2 pr-4">Utilisation</th>
              <th className="pb-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {data.agents.map((a: LiveAgentState) => (
              <tr key={a.agent_id} className={`border-b border-gray-800 ${rowColor(a.alert_state, a.utilization_score)}`}>
                <td className="py-2 pr-4 text-white font-medium">{a.agent_name}</td>
                <td className="py-2 pr-4 text-gray-300">{roleLabel[a.planned_role]}</td>
                <td className="py-2 pr-4 text-gray-300">{roleLabel[a.current_role]}</td>
                <td className="py-2 pr-4">{presenceDot(a.presence_status, a.presence_stale)}</td>
                <td className="py-2 pr-4 text-gray-300">{a.active_chats_estimated}</td>
                <td className="py-2 pr-4 text-gray-300">{a.assigned_open_tickets}</td>
                <td className="py-2 pr-4 text-gray-300">{a.overdue_assigned_tickets}</td>
                <td className="py-2 pr-4">{utilBar(a.utilization_score)}</td>
                <td className={`py-2 ${recColor[a.recommendation]}`}>{recLabel[a.recommendation]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
