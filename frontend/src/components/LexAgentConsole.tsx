"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  createQuery,
  getQuery,
  streamQueryEvents,
  type NodeEvent,
  type QueryResponse,
} from "@/lib/api";

const EXAMPLES = [
  "My landlord kept my entire security deposit for normal wear and tear in Texas.",
  "I received a 3-day eviction notice in California but the landlord never repaired the heater.",
  "Can I break my Texas lease early if my job relocated me out of state?",
  "My California apartment has had no hot water for two weeks. What can I do?",
];

const ANSWER_FIELDS: { key: keyof NonNullable<QueryResponse["answer"]>; label: string }[] = [
  { key: "rights", label: "Your rights" },
  { key: "obligations", label: "Your obligations" },
  { key: "reasoning", label: "Reasoning" },
  { key: "confidence", label: "Confidence" },
  { key: "disclaimer", label: "Disclaimer" },
];

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString();
  } catch {
    return iso;
  }
}

function NodeBadge({ node }: { node: string }) {
  const colors: Record<string, string> = {
    parse_query: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    retrieve: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
    validate_retrieval: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    reason: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
    extract_claims: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
    verify_citations: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    publish: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    refuse: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    budget_exceeded: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[node] ?? "bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-200"}`}
    >
      {node}
    </span>
  );
}

export function LexAgentConsole() {
  const [question, setQuestion] = useState(EXAMPLES[0]);
  const [runId, setRunId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "completed" | "failed">("idle");
  const [events, setEvents] = useState<(NodeEvent & { at: string })[]>([]);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    eventsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const handleSubmit = useCallback(async () => {
    if (!question.trim() || status === "running") return;
    setStatus("running");
    setEvents([]);
    setResult(null);
    setError(null);
    setRunId(null);

    try {
      const { id } = await createQuery(question);
      setRunId(id);

      streamQueryEvents(
        id,
        {
          onEvent: (event) => {
            setEvents((prev) => [...prev, { ...event, at: new Date().toISOString() }]);
          },
          onEnd: async () => {
            const final = await getQuery(id);
            setResult(final);
            setStatus(final.status === "completed" ? "completed" : "failed");
          },
          onError: (err) => {
            setError(err.message);
            setStatus("failed");
          },
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setStatus("failed");
    }
  }, [question, status]);

  const handleExample = useCallback((text: string) => {
    setQuestion(text);
  }, []);

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm dark:border-neutral-800 dark:bg-neutral-900">
        <label htmlFor="question" className="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Describe your rental situation
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={4}
          className="w-full resize-y rounded-lg border border-neutral-300 bg-white px-4 py-3 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-700 dark:bg-neutral-950 dark:text-neutral-100"
          placeholder="e.g., My landlord kept my security deposit..."
        />
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => handleExample(example)}
              className="rounded-full border border-neutral-200 bg-neutral-50 px-3 py-1 text-xs text-neutral-700 hover:bg-neutral-100 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700"
            >
              {example.slice(0, 40)}…
            </button>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-neutral-500">
            Public-domain statute excerpts only (TX Property Code chs. 24, 91, 92; CA Civil Code §§1941–1954).
          </p>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={status === "running" || !question.trim()}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-neutral-400 dark:bg-blue-700 dark:hover:bg-blue-600 dark:disabled:bg-neutral-600"
          >
            {status === "running" ? "Analyzing…" : "Ask LexAgent"}
          </button>
        </div>
      </section>

      {runId && (
        <div className="text-xs text-neutral-500">
          Run ID: <code className="rounded bg-neutral-100 px-1 py-0.5 dark:bg-neutral-800">{runId}</code>
        </div>
      )}

      {events.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
            Reasoning trace
          </h2>
          <div className="space-y-3">
            {events.map((event, index) => (
              <div
                key={`${event.node}-${index}`}
                className="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900"
              >
                <div className="flex items-center gap-2">
                  <NodeBadge node={event.node} />
                  <span className="text-xs text-neutral-400">{formatTimestamp(event.at)}</span>
                </div>
                {event.data && Object.keys(event.data).length > 0 && (
                  <pre className="mt-2 max-h-32 overflow-auto rounded bg-neutral-50 p-2 text-xs text-neutral-700 dark:bg-neutral-950 dark:text-neutral-300">
                    {JSON.stringify(event.data, null, 2)}
                  </pre>
                )}
              </div>
            ))}
            <div ref={eventsEndRef} />
          </div>
        </section>
      )}

      {result?.answer && (
        <section className="rounded-xl border border-green-200 bg-green-50 p-6 dark:border-green-900 dark:bg-green-950/30">
          <h2 className="mb-4 text-lg font-semibold text-green-900 dark:text-green-100">Answer</h2>
          <dl className="space-y-4">
            {ANSWER_FIELDS.map(({ key, label }) => {
              const value = result.answer?.[key];
              if (value === undefined || value === null) return null;
              return (
                <div key={key}>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-green-800 dark:text-green-300">
                    {label}
                  </dt>
                  <dd className="mt-1 text-sm text-green-900 dark:text-green-100">{String(value)}</dd>
                </div>
              );
            })}
          </dl>
          {result.answer.citations.length > 0 && (
            <div className="mt-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-green-800 dark:text-green-300">
                Citations
              </h3>
              <ul className="mt-1 space-y-2">
                {result.answer.citations.map((citation) => (
                  <li key={citation.source_id} className="text-sm text-green-900 dark:text-green-100">
                    <code className="rounded bg-green-100 px-1 py-0.5 text-xs dark:bg-green-900">
                      {citation.source_id}
                    </code>{" "}
                    <span className="text-xs text-green-800 dark:text-green-300">({citation.corpus})</span>
                    {citation.quoted_span && <blockquote className="mt-1 border-l-2 border-green-300 pl-3 italic">{citation.quoted_span}</blockquote>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {result?.error && (
        <section className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950/30">
          <h2 className="text-lg font-semibold text-red-900 dark:text-red-100">Run failed</h2>
          <p className="mt-2 text-sm text-red-800 dark:text-red-200">{result.error}</p>
        </section>
      )}

      {error && (
        <section className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950/30">
          <h2 className="text-lg font-semibold text-red-900 dark:text-red-100">Error</h2>
          <p className="mt-2 text-sm text-red-800 dark:text-red-200">{error}</p>
        </section>
      )}

      <p className="text-xs text-neutral-400">
        LexAgent is research software, not legal advice. Consult a licensed attorney for your situation.
      </p>
    </div>
  );
}
