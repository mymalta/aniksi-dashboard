import { useEffect, useRef, useState } from "react";
import { LiveOverview } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const RECONNECT_DELAY = 3000;

export function useDashboard() {
  const [overview, setOverview] = useState<LiveOverview | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch initial state via REST so the page isn't blank before first WS message
  useEffect(() => {
    fetch(`${API_URL}/dashboard/live`)
      .then((r) => r.json())
      .then(setOverview)
      .catch(() => null);
  }, []);

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(`${WS_URL}/ws/dashboard`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);

      ws.onmessage = (e) => {
        try {
          setOverview(JSON.parse(e.data));
        } catch {
          // ignore malformed frames
        }
      };

      ws.onclose = () => {
        setConnected(false);
        timerRef.current = setTimeout(connect, RECONNECT_DELAY);
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      wsRef.current?.close();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return { overview, connected };
}
