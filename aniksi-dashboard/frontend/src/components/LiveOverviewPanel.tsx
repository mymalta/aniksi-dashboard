import { LiveOverview } from "@/types";

const statusColors = {
  green: "bg-green-500",
  amber: "bg-amber-400",
  red: "bg-red-500",
};

const statusLabel = {
  green: "Normal",
  amber: "Pressure rising",
  red: "Critical — act now",
};

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center bg-gray-800 rounded-lg px-4 py-3 min-w-[110px]">
      <span className="text-2xl font-bold text-white">{value}</span>
      <span className="text-xs text-gray-400 text-center mt-1">{label}</span>
    </div>
  );
}

export function LiveOverviewPanel({ overview }: { overview: LiveOverview }) {
  const dot = statusColors[overview.status];
  const label = statusLabel[overview.status];
  const waitSec = Math.round(overview.avg_chat_wait_seconds);

  return (
    <section className="space-y-3">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-white">Live Operations</h2>
        <span className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium text-white ${dot}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-white/70 inline-block" />
          {label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        <Metric label="Scheduled" value={overview.scheduled_agents} />
        <Metric label="Online" value={overview.online_agents} />
        <Metric label="On break" value={overview.agents_on_break} />
        <Metric label="Active chats" value={overview.active_chats} />
        <Metric label="Queued chats" value={overview.queued_chats} />
        <Metric label="Open tickets" value={overview.open_tickets} />
        <Metric label="Unassigned" value={overview.unassigned_tickets} />
        <Metric label="Overdue tickets" value={overview.overdue_tickets} />
        <Metric label="Avg wait" value={`${waitSec}s`} />
      </div>
    </section>
  );
}
