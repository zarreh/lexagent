import { TraceEventSchema, type TraceEvent } from "./schemas";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number
  ) {
    super(message);
  }
}

export type TraceEventHandlers = {
  onEvent: (event: TraceEvent) => void;
  onEnd: () => void;
  onError: () => void;
};

/** Subscribes to GET /ask/skeleton/events (SSE). Returns a cleanup function. */
export function streamSkeletonEvents(
  message: string,
  handlers: TraceEventHandlers
): () => void {
  const source = new EventSource(
    `${API_BASE}/ask/skeleton/events?message=${encodeURIComponent(message)}`
  );
  source.onmessage = (messageEvent) => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(messageEvent.data as string);
    } catch {
      handlers.onError();
      return;
    }
    const result = TraceEventSchema.safeParse(parsed);
    if (!result.success) {
      handlers.onError();
      return;
    }
    handlers.onEvent(result.data);
    if (result.data.node === "__end__") {
      source.close();
      handlers.onEnd();
    }
  };
  source.onerror = () => {
    source.close();
    handlers.onError();
  };
  return () => source.close();
}
