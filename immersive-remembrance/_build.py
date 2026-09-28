"""Build the Immersive Remembrance site: wraps _pages/*.html in the shared header/footer.
Run: python _build.py   (from this folder). Edit content in _pages/, never the generated *.html.
Each fragment starts with:  <!-- nav-key | Page title | meta description -->
"""
import pathlib, re

ROOT = pathlib.Path(__file__).parent
NAV = [("index", "Home"), ("about", "About"), ("research", "Research"), ("archive", "3D Archive"),
       ("team", "Team"), ("news", "News"), ("resources", "Resources")]
BASE = "https://educatian.github.io/immersive-remembrance/"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Immersive Remembrance">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}img/hero-poster.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' fill='%230e141f' stroke='%23d8bd84' stroke-width='2'/%3E%3Ctext x='16' y='22' font-size='17' text-anchor='middle' fill='%23d8bd84' font-family='Georgia'%3EIR%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="./"><span class="mark">IR</span><span><b>Immersive Remembrance</b><small>Living Archive VR · IMLS</small></span></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav" onclick="var n=document.getElementById('nav');this.setAttribute('aria-expanded',n.classList.toggle('open'))">Menu</button>
    <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <h4>Immersive Remembrance</h4>
        <p style="color:#aab2bf;margin:0">AI-Driven Archival Retrieval for VR Learning. An applied research project of The University of Alabama with the Alabama Veterans Museum &amp; Archives, Athens, AL.</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>{foot_nav}</ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li>Jewoong Moon, Principal Investigator</li>
          <li><a href="mailto:jmoon19@ua.edu">jmoon19@ua.edu</a></li>
          <li><a href="https://educatian.github.io/adie/">AdDIE Lab</a></li>
          <li><a href="../">Educatian home</a></li>
        </ul>
      </div>
    </div>
    <div class="funders">
      <a href="https://www.imls.gov/"><img class="imls" src="img/imls_logo_2c.jpg" alt="Institute of Museum and Library Services"></a>
      <a href="https://educatian.github.io/adie/"><img class="adie" src="img/addie-lockup-horizontal.svg" alt="AdDIE Lab: Adaptive Design of Immersive E-Learning"></a>
      <a class="partner" href="https://www.alabamaveteransmuseum.com/">In partnership with Alabama Veterans Museum &amp; Archives</a>
    </div>
    <p class="ack">This project was made possible in part by the Institute of Museum and Library Services (MG-260576-OMS-26). The views, findings, conclusions or recommendations expressed in this website do not necessarily represent those of the Institute of Museum and Library Services.</p>
  </div>
</footer>
</body>
</html>
"""


def href(key):
    return "./" if key == "index" else f"{key}.html"


cur = ' aria-current="page"'
for src in sorted((ROOT / "_pages").glob("*.html")):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"<!--\s*(\w+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*-->\n", text)
    key, title, desc = m.groups()
    nav = "".join(f'<a href="{href(k)}"{cur if k == key else ""}>{label}</a>' for k, label in NAV)
    foot_nav = "".join(f'<li><a href="{href(k)}">{label}</a></li>' for k, label in NAV)
    url = BASE if key == "index" else f"{BASE}{key}.html"
    page = HEAD.format(title=title, desc=desc, url=url, base=BASE, nav=nav) + text[m.end():] + FOOT.format(foot_nav=foot_nav)
    (ROOT / f"{key}.html").write_text(page, encoding="utf-8")
    print("built", key)
