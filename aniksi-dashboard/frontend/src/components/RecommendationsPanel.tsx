import { Recommendation } from "@/types";

const actionLabel: Record<string, string> = {
  move_flex_to_chat: "Move to Chat",
  move_flex_to_ticket: "Move to Tickets",
  protect_from_ticket_intake: "Protect — no new tickets",
};

const actionColor: Record<string, string> = {
  move_flex_to_chat: "border-blue-500 bg-blue-900/20",
  move_flex_to_ticket: "border-amber-500 bg-amber-900/20",
  protect_from_ticket_intake: "border-red-500 bg-red-900/20",
};

function ConfidencePips({ value }: { value: number }) {
  const filled = Math.round(value * 5);
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} className={`w-2 h-2 rounded-full ${i < filled ? "bg-green-400" : "bg-gray-600"}`} />
      ))}
    </div>
  );
}

export function RecommendationsPanel({ recommendations }: { recommendations: Recommendation[] }) {
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold text-white">
        Flex Recommendations
        {recommendations.length > 0 && (
          <span className="ml-2 text-sm font-normal text-amber-400">{recommendations.length} action{recommendations.length > 1 ? "s" : ""}</span>
        )}
      </h2>

      {recommendations.length === 0 ? (
        <p className="text-gray-500 text-sm">No action needed — load is balanced.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {recommendations.map((r, i) => (
            <div key={i} className={`rounded-xl border p-4 space-y-2 ${actionColor[r.action] ?? "border-gray-600 bg-gray-800"}`}>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">{r.agent_name}</span>
                <span className="text-xs text-gray-300 bg-gray-700 rounded px-2 py-0.5">
                  {actionLabel[r.action] ?? r.action}
                </span>
              </div>
              <p className="text-sm text-gray-300">{r.reason}</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Confidence</span>
                <ConfidencePips value={r.confidence} />
                <span className="text-xs text-gray-400">{Math.round(r.confidence * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
