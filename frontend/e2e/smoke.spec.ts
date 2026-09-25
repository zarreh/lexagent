import { expect, test } from "@playwright/test";

test.describe("LexAgent UI smoke", () => {
  test("renders the title and example buttons", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "LexAgent" })).toBeVisible();
    await expect(page.getByText("Grounded rental-law reasoning")).toBeVisible();
    await expect(page.getByRole("button", { name: /Ask LexAgent/ })).toBeVisible();
    await expect(page.getByRole("button").first()).toBeVisible();
  });

  test("clicking an example populates the question textarea", async ({ page }) => {
    await page.goto("/");
    const textarea = page.getByPlaceholder("e.g., My landlord kept my security deposit...");
    await expect(textarea).toBeVisible();
    const exampleButton = page.getByRole("button").nth(1);
    await exampleButton.click();
    const value = await textarea.inputValue();
    expect(value.length).toBeGreaterThan(10);
  });
});
