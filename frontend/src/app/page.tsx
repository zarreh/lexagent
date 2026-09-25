import { LexAgentConsole } from "@/components/LexAgentConsole";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl p-8 font-sans">
      <h1 className="text-2xl font-bold">LexAgent</h1>
      <p className="mt-2 text-sm text-neutral-500">
        Grounded rental-law reasoning over statute and synthetic precedent —
        streamed node-by-node.
      </p>

      <div className="mt-6">
        <LexAgentConsole />
      </div>
    </main>
  );
}
