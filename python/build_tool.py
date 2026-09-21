"""
Assemble the public explorer: inline the payload into the template.

The page carries its own data so it works when opened as a file and on any
static host. The template is a fragment (<title>, <style>, markup, <script>);
this script wraps it in a complete HTML document.

Writes tool/index.html.
"""

from __future__ import annotations

import json

import config

TEMPLATE = config.ROOT / "tool" / "index.template.html"
DATA = config.ROOT / "tool" / "model_data.json"
OUT = config.ROOT / "tool" / "index.html"
MARKER = "__MODEL_DATA__"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A lifetime cost-of-aging calculator: from \
health at 65, expected years in each health state, lifetime Medicare and \
out-of-pocket cost, the worst-case tail, and what a Medicare Hospital \
Insurance shortfall would pass on to households, built on the Health and \
Retirement Study and the Medicare Current Beneficiary Survey.">
<meta name="author" content="Oluwatosin Dorcas Babalola, Oluwakemi Elizabeth Iroko, Doris Ansah">
<meta property="og:title" content="The Long Road">
<meta property="og:description" content="What aging costs Medicare and you, \
health path by health path.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,\
%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E\
%3Ctext y='.9em' font-size='90'%3E%F0%9F%9B%A4%3C/text%3E%3C/svg%3E">
<style>
  html{-webkit-text-size-adjust:100%}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
"""
TAIL = "\n</body>\n</html>\n"


def main():
    template = TEMPLATE.read_text()
    data = json.loads(DATA.read_text())
    if MARKER not in template:
        raise SystemExit(f"{MARKER} not found in template")
    template = template.replace(MARKER, json.dumps(data, separators=(",", ":")))
    cut = template.find("<header")
    if cut < 0:
        raise SystemExit("template has no <header>")
    html = HEAD + template[:cut] + "</head>\n<body>\n" + template[cut:] + TAIL
    OUT.write_text(html)
    print(f"wrote {OUT.relative_to(config.ROOT)} ({OUT.stat().st_size / 1024:,.0f} KB)")


if __name__ == "__main__":
    main()
