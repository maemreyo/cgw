"""Turn a recorded cgw session (text) into an animated terminal SVG. Usage: build_svg.py session.txt out.svg"""
import sys, html, textwrap
src, out = sys.argv[1], sys.argv[2]
W, PAD, LH, FS, COLS = 980, 26, 20, 13.5, 112
raw = open(src).read().rstrip("\n").split("\n")
lines = []  # (text, kind)
for l in raw:
    if l.startswith("$ "): kind = "cmd"
    elif l.startswith("==>"): kind = "step"
    elif l.startswith("[dry-run]"): kind = "dry"
    elif l.startswith("* "): kind = "cur"
    else: kind = "out"
    if len(l) > COLS:
        parts = textwrap.wrap(l, COLS, subsequent_indent="    ", break_long_words=False)
    else: parts = [l]
    for i, p in enumerate(parts): lines.append((p, kind if i == 0 else kind))
top = 52
H = top + len(lines) * LH + 22
T = 34.0                       # seconds per loop
# reveal times: commands take longer (typing pause), outputs follow quickly
t, times = 0.8, []
for text, kind in lines:
    if kind == "cmd": t += 0.9
    elif text == "": t += 0.15
    else: t += 0.28
    times.append(t)
end = t + 3.5
T = max(T, end + 1.5)
colors = {"cmd": "#e6edf3", "step": "#79c0ff", "dry": "#8b949e", "cur": "#7ee787", "out": "#c9d1d9"}
css = ["text{font:%spx ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre}"%FS,
       ".l{opacity:0;animation-duration:%.1fs;animation-iteration-count:infinite;animation-timing-function:step-end}"%T,
       "@media (prefers-reduced-motion:reduce){.l{opacity:1!important;animation:none!important}}"]
body = []
for i, ((text, kind), ts) in enumerate(zip(lines, times)):
    p0, p1 = ts / T * 100, end / T * 100
    css.append("@keyframes k%d{0%%{opacity:0}%.2f%%{opacity:1}%.2f%%{opacity:1}%.2f%%{opacity:0}100%%{opacity:0}}" % (i, p0, p1, min(p1 + 0.01, 99.99)))
    css.append("#a%d{animation-name:k%d}" % (i, i))
    y = top + i * LH
    t_esc = html.escape(text)
    if kind == "cmd":
        t_esc = '<tspan fill="#7ee787">$</tspan>' + html.escape(text[1:])
    body.append('<text id="a%d" class="l" x="%d" y="%d" fill="%s">%s</text>' % (i, PAD, y, colors[kind], t_esc))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Terminal demo of cgw: register an account, take a tunnel id from the clipboard, list accounts and preview a switch with DRY=1. Sample data.">
<title>cgw demo (dry-run, sample data)</title>
<style>{"".join(css)}</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
<rect width="{W}" height="34" rx="10" fill="#161b22"/><rect y="24" width="{W}" height="10" fill="#161b22"/>
<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/><circle cx="60" cy="17" r="6" fill="#27c93f"/>
<text x="{W//2}" y="22" fill="#8b949e" text-anchor="middle" style="opacity:1;animation:none;font-size:12px">cgw — demo with sample IDs (DRY=1: nothing is changed)</text>
{"".join(body)}
</svg>'''
open(out, "w").write(svg)
print("svg", W, H, "lines", len(lines), "loop %.1fs" % T)
