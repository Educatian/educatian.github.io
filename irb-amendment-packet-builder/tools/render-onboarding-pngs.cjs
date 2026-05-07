const { chromium } = require("playwright");
const path = require("path");

const outDir = path.resolve(__dirname, "../assets");

const frames = [
  {
    id: "onboarding-01",
    title: "1. Install Obsidian and Create a Safe Vault",
    subtitle: "Start with a local-first workspace. Keep the vault public-safe: project notes and pointers only.",
    cards: [
      ["Download Obsidian", "Use the official installer and create a local vault."],
      ["Create folders", "wiki/entities, wiki/irb, wiki/sources, wiki/logs."],
      ["Add TeachPlay note", "Study purpose, population, repo link, data categories."],
      ["Keep private data out", "No raw participant data, private consent forms, or sensitive emails."]
    ],
    footer: "Beginner rule: the vault is an index and drafting workspace, not the storage location for protected research records."
  },
  {
    id: "onboarding-02",
    title: "2. Build the Amendment Evidence Bundle",
    subtitle: "Before writing prose, collect the records that prove what changed.",
    cards: [
      ["Obsidian project note", "Purpose, participants, current status, open questions."],
      ["GitHub repo", "New features: surveys, uploads, telemetry, AI policy pages."],
      ["Approved IRB baseline", "Current protocol, consent, recruitment, instruments."],
      ["Survey / API records", "Qualtrics, REDCap, OSF, Canvas, or local CSV fields."]
    ],
    footer: "Ask Claude Code or Codex for an inventory first. Drafting starts only after missing evidence is visible."
  },
  {
    id: "onboarding-03",
    title: "3. Decide the Amendment Route",
    subtitle: "Use simple routing before writing HRP-502/503 language.",
    cards: [
      ["Cosmetic edit?", "Typos, contact details, minor wording only."],
      ["Administrative update?", "Personnel, recruitment logistics, dates, non-risk changes."],
      ["Amendment packet?", "New procedures, new data, new instruments, AI/API boundary."],
      ["Consult first?", "New population, sensitive data, unclear risk, retained free text."]
    ],
    footer: "If participants experience something new, or data crosses a new AI/API boundary, treat it as amendment work."
  },
  {
    id: "onboarding-04",
    title: "4. Generate, Review, and Verify the Packet",
    subtitle: "The output is a folder a human can inspect before using the institution's IRB system.",
    cards: [
      ["Draft packet", "Protocol delta, consent insert, recruitment update, data appendix."],
      ["PI review", "Confirm risk level, participant burden, data promises, attachments."],
      ["Playwright check", "Verify page, images, anchors, downloads, and smoke screenshot."],
      ["Manual submission", "Paste into Cayuse, Kuali, VERA, eRA, or local IRB system."]
    ],
    footer: "Do not automate final submission. Automation supports consistency; humans own the final judgment."
  }
];

function frameHtml(frame) {
  const cards = frame.cards.map(([head, body], i) => `
    <div class="card">
      <div class="num">${String(i + 1).padStart(2, "0")}</div>
      <h2>${head}</h2>
      <p>${body}</p>
    </div>`).join("");

  return `
  <section class="frame" id="${frame.id}">
    <div class="topline">
      <div class="label">IRB Amendment Packet Builder</div>
      <div class="tag">Beginner onboarding</div>
    </div>
    <h1>${frame.title}</h1>
    <p class="subtitle">${frame.subtitle}</p>
    <div class="flow">${cards}</div>
    <div class="footer">${frame.footer}</div>
  </section>`;
}

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{margin:0;background:#e7dccb;font-family:Inter,Arial,sans-serif;color:#182126}
  .stage{display:flex;flex-direction:column;gap:40px;padding:40px}
  .frame{
    width:1400px;height:900px;position:relative;overflow:hidden;
    background:#fffdf8;border:6px solid #182126;border-radius:34px;padding:58px 64px;
  }
  .frame::before{
    content:"";position:absolute;inset:0;opacity:.24;
    background-image:linear-gradient(rgba(24,33,38,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(24,33,38,.08) 1px,transparent 1px);
    background-size:42px 42px;pointer-events:none;
  }
  .topline{position:relative;display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}
  .label{font-size:19px;font-weight:900;letter-spacing:3px;text-transform:uppercase;color:#284c63}
  .tag{font-size:17px;font-weight:800;color:#b35c35;border:2px solid #b35c35;border-radius:999px;padding:9px 18px;background:#fff9f4}
  h1{position:relative;margin:0;max-width:1100px;font-size:60px;line-height:1.04;letter-spacing:0;font-weight:900}
  .subtitle{position:relative;margin:20px 0 38px;max-width:1120px;font-size:27px;line-height:1.38;color:#45545b}
  .flow{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-top:26px}
  .card{
    min-height:360px;background:#fff;border:3px solid #182126;border-radius:22px;padding:26px 24px;
    box-shadow:0 18px 0 rgba(40,76,99,.13);position:relative;
  }
  .card::after{
    content:"";position:absolute;right:-27px;top:150px;width:31px;height:30px;background:#284c63;
    clip-path:polygon(0 0,100% 50%,0 100%);
  }
  .card:last-child::after{display:none}
  .num{font-family:Consolas,monospace;font-weight:900;font-size:23px;color:#fff;background:#284c63;border-radius:14px;width:62px;height:48px;display:flex;align-items:center;justify-content:center;margin-bottom:24px}
  h2{font-size:34px;line-height:1.12;margin:0 0 16px;font-weight:900;letter-spacing:0}
  .card p{font-size:24px;line-height:1.36;margin:0;color:#4d5c62}
  .footer{
    position:absolute;left:64px;right:64px;bottom:54px;background:#f6ead4;border-left:10px solid #b4862e;
    border-radius:18px;padding:22px 26px;font-size:25px;line-height:1.32;font-weight:800;color:#3b3428;
  }
</style>
</head>
<body><main class="stage">${frames.map(frameHtml).join("")}</main></body>
</html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "load" });
  for (const frame of frames) {
    const locator = page.locator(`#${frame.id}`);
    await locator.screenshot({ path: path.join(outDir, `${frame.id}.png`), animations: "disabled" });
  }
  await browser.close();
  console.log(`Rendered ${frames.length} onboarding PNGs to ${outDir}`);
})();
