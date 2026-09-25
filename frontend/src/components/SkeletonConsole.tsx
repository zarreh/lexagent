"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { streamSkeletonEvents } from "@/lib/api";
import type { TraceEvent } from "@/lib/schemas";

export function SkeletonConsole() {
  const [message, setMessage] = useState("");
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [status, setStatus] = useState<"idle" | "streaming" | "done" | "error">(
    "idle"
  );

  const start = useCallback(() => {
    setEvents([]);
    setStatus("streaming");
    const cleanup = streamSkeletonEvents(message || "hello", {
      onEvent: (event) => setEvents((prev) => [...prev, event]),
      onEnd: () => setStatus("done"),
      onError: () => setStatus("error"),
    });
    return cleanup;
  }, [message]);

  useEffect(() => {
    const cleanup = start();
    return cleanup;
  }, [start]);

  const lastOutput = useMemo(
    () => events[events.length - 1]?.output ?? null,
    [events]
  );

  return (
    <section className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 rounded border border-neutral-300 px-3 py-2 text-sm"
        />
        <button
          onClick={start}
          disabled={status === "streaming"}
          className="rounded bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Stream
        </button>
      </div>

      <p className="text-sm text-neutral-500">
        Status: <span className="font-medium">{status}</span>
      </p>

      <div className="rounded border border-neutral-200 bg-neutral-50 p-4">
        <h2 className="text-sm font-semibold">Events</h2>
        <ul className="mt-2 space-y-1 text-sm font-mono">
          {events.map((event, index) => (
            <li key={index}>
              <span className="text-neutral-500">{event.node}:</span>{" "}
              {JSON.stringify(event.output)}
            </li>
          ))}
        </ul>
        {lastOutput !== null && (
          <p className="mt-4 text-sm">
            Last output: <code>{JSON.stringify(lastOutput)}</code>
          </p>
        )}
      </div>
    </section>
  );
}
