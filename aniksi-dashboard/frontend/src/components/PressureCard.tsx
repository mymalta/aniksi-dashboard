interface PressureCardProps {
  title: string;
  pressure: number;
  metrics: { label: string; value: string | number }[];
}

function PressureBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = value >= 0.8 ? "bg-red-500" : value >= 0.6 ? "bg-amber-400" : "bg-green-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">Pressure</span>
        <span className="text-white font-semibold">{pct}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div className={`h-2 rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export function PressureCard({ title, pressure, metrics }: PressureCardProps) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 space-y-4 flex-1 min-w-[220px]">
      <h3 className="text-base font-semibold text-white">{title}</h3>
      <PressureBar value={pressure} />
      <ul className="space-y-1.5">
        {metrics.map(({ label, value }) => (
          <li key={label} className="flex justify-between text-sm">
            <span className="text-gray-400">{label}</span>
            <span className="text-white">{value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
