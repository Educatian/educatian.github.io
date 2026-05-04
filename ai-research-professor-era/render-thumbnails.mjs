import { chromium } from "playwright";
import path from "node:path";
import { mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";

const root = "C:/Users/jewoo/Desktop/_PTs/2026-05-03_ai-era-professor-survival";
const outDir = path.join(root, "thumbnails");
const baseUrl = pathToFileURL(path.join(root, "index.html")).href;

const targets = [
  { slide: 1, name: "thumb-01-title.png" },
  { slide: 9, name: "thumb-09-overview-full.png" },
  { slide: 12, name: "thumb-12-weekly-workflow.png" },
  { slide: 14, name: "thumb-14-pr-checklist.png" },
  { slide: 15, name: "thumb-15-ai-prompts.png" },
];

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
});

for (const target of targets) {
  const page = await browser.newPage({
    viewport: { width: 1600, height: 900 },
    deviceScaleFactor: 1.5,
  });
  await page.goto(`${baseUrl}?slide=${target.slide}`, { waitUntil: "load" });
  await page.screenshot({
    path: path.join(outDir, target.name),
    type: "png",
  });
  await page.close();
}

await browser.close();
console.log(`Rendered ${targets.length} thumbnails to ${outDir}`);
