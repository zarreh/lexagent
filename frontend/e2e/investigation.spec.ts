import { expect, test } from "@playwright/test";

const ANSWER = {
  rights: "Refund within 30 days.",
  obligations: "Provide a forwarding address.",
  reasoning: "Section 92.103 requires refund within 30 days.",
  citations: [
    { source_id: "tx-prop-92.103", corpus: "statute", quoted_span: "shall refund a security deposit" },
  ],
  confidence: "high",
  referral_triggered: false,
  disclaimer: "Research only.",
};

test("streams node events and renders the cited answer", async ({ page }) => {
  await page.route("**/api/queries", async (route) => {
    await route.fulfill({ status: 202, json: { id: "run-1", status: "running" } });
  });
  await page.route("**/api/queries/run-1/events", async (route) => {
    const body = [
      `event: parse_query\ndata: ${JSON.stringify({ parsed_query: { jurisdiction: "TX" } })}\n\n`,
      `event: retrieve\ndata: ${JSON.stringify({ retrieved_sources: [] })}\n\n`,
      `event: publish\ndata: ${JSON.stringify({ answer: ANSWER })}\n\n`,
      `event: done\ndata: {"status": "completed"}\n\n`,
    ].join("");
    await route.fulfill({ status: 200, contentType: "text/event-stream", body });
  });
  await page.route("**/api/queries/run-1", async (route) => {
    await route.fulfill({
      json: {
        id: "run-1",
        question: "q",
        status: "completed",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:01Z",
        outcome_kind: "answer",
        answer: ANSWER,
        error: null,
      },
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Ask LexAgent" }).click();

  await expect(page.getByText("parse_query", { exact: true })).toBeVisible();
  await expect(page.getByText("publish", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Answer" })).toBeVisible();
  await expect(page.getByText("tx-prop-92.103", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Error" })).toHaveCount(0);
});
