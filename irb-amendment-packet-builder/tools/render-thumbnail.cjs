const { chromium } = require("playwright");
const path = require("path");

const out = path.resolve(__dirname, "../assets/thumbnail.png");

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{margin:0;background:#f2eadc;font-family:Inter,Arial,sans-serif;color:#182126}
  .thumb{
    width:1200px;height:630px;position:relative;overflow:hidden;padding:48px 58px;
    background:#fffdf8;
  }
  .thumb::before{
    content:"";position:absolute;inset:0;opacity:.24;
    background-image:linear-gradient(rgba(24,33,38,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(24,33,38,.08) 1px,transparent 1px);
    background-size:38px 38px;
  }
  .thumb::after{
    content:"";position:absolute;right:-90px;top:-90px;width:380px;height:380px;border-radius:50%;
    border:58px solid rgba(179,92,53,.13);
  }
  .content{position:relative;z-index:1}
  .kicker{font-size:18px;font-weight:900;letter-spacing:4px;text-transform:uppercase;color:#284c63;margin-bottom:24px}
  h1{font-size:74px;line-height:.98;letter-spacing:0;margin:0;font-weight:900;max-width:820px}
  .serif{font-family:Georgia,serif;font-style:italic;font-weight:400;color:#b35c35}
  .sub{font-size:28px;line-height:1.28;color:#3d4c52;margin:24px 0 30px;max-width:880px}
  .flow{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;width:920px;margin-top:18px}
  .card{
    min-height:132px;background:#fff;border:3px solid #182126;border-radius:18px;padding:17px 16px;
    box-shadow:0 10px 0 rgba(40,76,99,.13);position:relative;
  }
  .card::after{
    content:"";position:absolute;right:-17px;top:53px;width:20px;height:22px;background:#284c63;
    clip-path:polygon(0 0,100% 50%,0 100%);
  }
  .card:last-child::after{display:none}
  .num{font-family:Consolas,monospace;background:#284c63;color:#fff;border-radius:10px;width:42px;height:32px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px;margin-bottom:12px}
  .card h2{font-size:23px;line-height:1.04;margin:0 0 7px;font-weight:900}
  .card p{font-size:15px;line-height:1.22;margin:0;color:#506066}
  .badge{
    position:absolute;right:58px;top:128px;background:#f6ead4;border-left:8px solid #b4862e;
    border-radius:16px;padding:18px 20px;width:300px;font-size:20px;line-height:1.18;font-weight:900;color:#2f2a21;
  }
  .brand{position:absolute;right:58px;top:50px;font-size:16px;font-weight:900;letter-spacing:3px;text-transform:uppercase;color:#b35c35;border:2px solid #b35c35;border-radius:999px;padding:10px 16px;background:#fff9f4}
</style>
</head>
<body>
  <main class="thumb">
    <div class="brand">Educatian Guide</div>
    <div class="content">
      <div class="kicker">Obsidian + GitHub + Claude Code</div>
      <h1>IRB Amendment <span class="serif">Packet Builder</span></h1>
      <p class="sub">Turn project changes into protocol deltas, consent language, recruitment scripts, and data-security appendices.</p>
      <section class="flow" aria-label="workflow">
        <div class="card"><div class="num">01</div><h2>Vault</h2><p>public-safe project memory</p></div>
        <div class="card"><div class="num">02</div><h2>Evidence</h2><p>repo, baseline docs, instruments</p></div>
        <div class="card"><div class="num">03</div><h2>Route</h2><p>minor edit, amendment, consult first</p></div>
        <div class="card"><div class="num">04</div><h2>Packet</h2><p>human-reviewed IRB drafts</p></div>
      </section>
    </div>
    <div class="badge">TeachPlay worked example<br>HRP-502/503-style drafts</div>
  </main>
</body>
</html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: "load" });
  await page.locator(".thumb").screenshot({ path: out, animations: "disabled" });
  await browser.close();
  console.log(`Rendered thumbnail to ${out}`);
})();
