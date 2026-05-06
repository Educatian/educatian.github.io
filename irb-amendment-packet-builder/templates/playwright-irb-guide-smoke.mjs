import { chromium } from "playwright";

const baseUrl = process.env.BASE_URL || "http://127.0.0.1:8765/irb-amendment-packet-builder/";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });

await page.goto(baseUrl, { waitUntil: "networkidle" });
await page.getByRole("heading", { name: /IRB Amendment/i }).waitFor();

const requiredText = [
  "Obsidian",
  "TeachPlay",
  "HRP-502/503-style",
  "45 CFR 46.111",
  "AI data-flow register",
  "Public-safe templates"
];

for (const text of requiredText) {
  const visible = await page.getByText(text, { exact: false }).first().isVisible();
  if (!visible) throw new Error(`Missing visible text: ${text}`);
}

const images = await page.locator("figure.image-frame img").all();
if (images.length < 5) {
  throw new Error(`Expected at least 5 embedded workflow images, found ${images.length}`);
}

for (const image of images) {
  const src = await image.getAttribute("src");
  const box = await image.boundingBox();
  if (!box || box.width < 200 || box.height < 100) {
    throw new Error(`Image failed visible size check: ${src}`);
  }
}

const links = await page.locator("a[href^='templates/']").all();
for (const link of links) {
  const href = await link.getAttribute("href");
  const response = await page.request.get(new URL(href, baseUrl).toString());
  if (!response.ok()) throw new Error(`Template link failed: ${href} -> ${response.status()}`);
}

await page.screenshot({ path: "irb-amendment-packet-builder-smoke.png", fullPage: true, animations: "disabled" });
await browser.close();

console.log(`OK ${baseUrl}`);
