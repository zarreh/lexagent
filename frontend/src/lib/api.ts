import type { paths } from "./api-types";
import { TraceEventSchema, type TraceEvent } from "./schemas";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

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
    `${API_BASE}/api/ask/skeleton/events?message=${encodeURIComponent(message)}`
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

export type QueryResponse =
  paths["/queries/{run_id}"]["get"]["responses"][200]["content"]["application/json"];

export interface NodeEvent {
  node: string;
  data: Record<string, unknown> | null;
}

export async function createQuery(question: string): Promise<{ id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/queries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`Failed to start query: ${response.statusText}`);
  }
  return response.json();
}

export async function getQuery(runId: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/queries/${runId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch query: ${response.statusText}`);
  }
  return response.json();
}

export type QueryEventHandlers = {
  onEvent: (event: NodeEvent) => void;
  onEnd: () => void;
  onError: (error: Error) => void;
};

/** Subscribes to GET /queries/{run_id}/events (SSE). Returns a cleanup function. */
export function streamQueryEvents(
  runId: string,
  handlers: QueryEventHandlers
): () => void {
  const source = new EventSource(`${API_BASE}/api/queries/${runId}/events`);

  source.addEventListener("message", (messageEvent) => {
    if (messageEvent.type === "done") {
      source.close();
      handlers.onEnd();
      return;
    }
    let data: Record<string, unknown> | null = null;
    if (messageEvent.data) {
      try {
        data = JSON.parse(messageEvent.data) as Record<string, unknown>;
      } catch {
        data = null;
      }
    }
    handlers.onEvent({ node: messageEvent.type, data });
  });

  source.addEventListener("error", () => {
    source.close();
    handlers.onError(new Error("Event stream closed unexpectedly"));
  });

  source.onerror = () => {
    source.close();
    handlers.onError(new Error("Event stream error"));
  };

  return () => source.close();
}
