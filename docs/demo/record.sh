#!/bin/bash
# Records a real `cgw` session against a sandboxed HOME with sample IDs (nothing real is touched),
# then builds docs/demo.svg and docs/social-preview.png. Needs macOS (pbcopy) and Google Chrome.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
D="$(mktemp -d)"; export HOME="$D/home"
mkdir -p "$HOME/.codex-chatgpt-web/versions/6.1.5-darwin-arm64" "$HOME/.codex-chatgpt-web/secrets"
echo '{"tunnel":{"tunnelId":"tunnel_0123456789abcdef0123456789abcdef"}}' > "$HOME/.codex-chatgpt-web/config.json"
printf 'sk-demo-not-a-real-key' > "$HOME/.codex-chatgpt-web/secrets/tunnel-runtime-automatic.key"
C="$ROOT/cgw"; OUT="$D/session.txt"; : > "$OUT"
run() { echo "\$ cgw ${*}" >> "$OUT"; "$C" "$@" >> "$OUT" 2>&1 || true; echo >> "$OUT"; }
run version
run adopt personal
printf 'tunnel_fedcba9876543210fedcba9876543210' | pbcopy
run clip tunnel work
pbcopy < /dev/null
run list
echo '$ DRY=1 cgw use work' >> "$OUT"; DRY=1 "$C" use work >> "$OUT" 2>&1 || true
sed -i '' "s#$D/home#~#g" "$OUT"
python3 "$ROOT/docs/demo/build_svg.py" "$OUT" "$ROOT/docs/demo.svg"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=1280,640 \
  --screenshot="$ROOT/docs/social-preview.png" "file://$ROOT/docs/demo/social-preview.html" >/dev/null 2>&1
rm -rf "$D"; echo "wrote docs/demo.svg and docs/social-preview.png"
