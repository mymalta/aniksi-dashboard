"use client";
import { useDashboard } from "@/hooks/useDashboard";
import { LiveOverviewPanel } from "@/components/LiveOverviewPanel";
import { AgentBoard } from "@/components/AgentBoard";
import { PressureCard } from "@/components/PressureCard";
import { RecommendationsPanel } from "@/components/RecommendationsPanel";

export default function DashboardPage() {
  const { overview, connected } = useDashboard();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <h1 className="font-semibold text-white tracking-tight">Aniksi Operations</h1>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-gray-500"}`} />
          {connected ? "Live" : "Reconnecting..."}
          {overview && (
            <span className="ml-3">
              Updated {new Date(overview.generated_at).toLocaleTimeString()}
            </span>
          )}
        </div>
      </header>

      <main className="px-6 py-6 space-y-8 max-w-screen-2xl mx-auto">
        {!overview ? (
          <p className="text-gray-500">Connecting to dashboard...</p>
        ) : (
          <>
            {/* Panel 1 */}
            <LiveOverviewPanel overview={overview} />

            {/* Panels 3 + 4: pressure side by side */}
            <div className="flex flex-wrap gap-4">
              <PressureCard
                title="Chat Pressure"
                pressure={overview.chat_pressure}
                metrics={[
                  { label: "Queued chats", value: overview.queued_chats },
                  { label: "Active chats", value: overview.active_chats },
                  { label: "Avg wait", value: `${Math.round(overview.avg_chat_wait_seconds)}s` },
                ]}
              />
              <PressureCard
                title="Ticket Pressure"
                pressure={overview.ticket_pressure}
                metrics={[
                  { label: "Open tickets", value: overview.open_tickets },
                  { label: "Unassigned", value: overview.unassigned_tickets },
                  { label: "Overdue", value: overview.overdue_tickets },
                ]}
              />
            </div>

            {/* Panel 5 */}
            <RecommendationsPanel recommendations={overview.recommendations} />

            {/* Panel 2 */}
            <AgentBoard />
          </>
        )}
      </main>
    </div>
  );
}
