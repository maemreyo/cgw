# Agent runbook: install / update a Codex Web GPT tunnel with `cgw`

You are an AI agent. The user sent you this file with a request such as "install and update the new tunnel".
**Run this as a guided conversation: one step at a time, in the user's language.** The user must not need to
remember any command, path or ID. Each step: say what you are doing, do it, tell the user the *one* thing you need
from them (a click, a copy, a yes), then wait. Never dump the whole plan at them.

Target: macOS, [codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web) ("Codex Web GPT" launcher).

## Ground rules

- **Secrets never go through chat.** The user copies the key (⌘C); you read it from the clipboard with
  `cgw clip key`, which verifies it, stores it 0600 and clears the clipboard. Never ask the user to paste a key or
  run `printf`/`echo` with one. Never print a key.
- **Do not create accounts, API keys or tunnels yourself** (not in a browser either). The user clicks "Create"; you guide.
- `setup` shows an "independent, unofficial software … automates your ChatGPT web session" notice.
  Ask the user to accept it (show the sentence). Only after a clear yes run with `CGW_ACK=1`. Ask again each run.
- Never delete `~/.codex-chatgpt-web/accounts/` or `~/Library/Application Support/Codex Web GPT/` (saved logins).
- `cgw use` quits and reopens the launcher and restarts the tunnel (~1–2 min). Warn the user before running it.
- If an interactive question tool exists (e.g. AskUserQuestion), use it for choices; otherwise ask in plain text.

## Script (follow in order)

### 1. Preflight (silent)
```bash
ls /Applications/"Codex Web GPT.app" ~/.codex-chatgpt-web/versions; which cgw; cgw list
```
Decide silently which of steps 2–3 are needed. Tell the user one line: what's installed and what you'll do.

### 2. Launcher: install or update (skip if already latest)
Check latest: `gh release view -R miuuyy/codex-chatgpt-web --json tagName --jq .tagName` (or the releases page) vs
`ls ~/.codex-chatgpt-web/versions`. If outdated/missing, say "I'll update Codex Web GPT to vX; it will close for a moment", then:
```bash
osascript -e 'tell application "Codex Web GPT" to quit'      # wait until pgrep -x "Codex Web GPT" is empty
curl -fsSL https://github.com/miuuyy/codex-chatgpt-web/releases/latest/download/install-launcher.sh -o /tmp/install-launcher.sh
# skim it, then:
sh /tmp/install-launcher.sh                                  # verifies SHA-256, keeps logins, reopens the app
```

### 3. cgw: install if missing
```bash
git clone https://github.com/maemreyo/cgw ~/Documents/projects/cgw && ~/Documents/projects/cgw/install.sh
```
If `cgw list` is empty but `~/.codex-chatgpt-web/config.json` exists, ask: "Máy đang chạy account nào? Đặt tên gì?" then
`cgw adopt <name>` — otherwise the current ChatGPT login would be lost on the first switch.

### 4. Which account? (ask)
Show `cgw list` and ask: update the tunnel of an existing account, or add a new account? Get a short label.
For a new label also ask: "Account ChatGPT này đã đăng nhập sẵn ở launcher chưa?" (it will be asked to sign in during step 7 anyway).

### 5. Tunnel id — user copies, you read
1. `open "https://platform.openai.com/settings/organization/tunnels"`
2. Tell the user: *"Mở đúng organization của account này (góc trên-trái), tạo tunnel mới nếu chưa có (Create), rồi bấm icon copy cạnh ID `tunnel_…` và nhắn mình 'xong'."*
3. After "xong": `cgw clip tunnel <label>` → prints the id. Show it back and ask "đúng tunnel này chứ?" (the name column is visible to them).
If it fails with "clipboard does not hold a tunnel id", ask them to click copy again.

### 6. Runtime key — user creates + copies, you read
1. `open "https://platform.openai.com/settings/organization/api-keys"`
2. Tell the user, concisely: *"Cùng organization và workspace với tunnel. Create new secret key → đặt tên (vd `codex-tunnel`) → quyền Restricted: **Tunnels = Read + Use** → Create. Bấm copy key (⌘C) và nhắn 'xong'. Đừng dán vào chat."*
3. After "xong": `cgw clip key <label>`.
   - `verified (HTTP 200)` → continue.
   - `HTTP 401/403` → key is from another org/workspace or lacks permission. Explain, tell them to create another, repeat.
   - "does not look like a runtime key" → they copied something else; ask to copy again right after creation (keys are shown once).

### 7. Apply
Say what will happen (launcher closes/reopens, ~2 min) and show the notice from "Ground rules"; ask for the yes. Then:
```bash
CGW_ACK=1 cgw use <label>          # DRY=1 CGW_ACK=1 cgw use <label> previews
```
- No saved login for this label → the launcher opens a ChatGPT sign-in. Tell the user: *"Đăng nhập ChatGPT trong cửa sổ Codex Web GPT vừa mở, xong nhắn mình."* Wait. If setup timed out, re-run `cgw use <label>` (safe to repeat).
- Do not interrupt midway; re-running recovers.

### 8. Verify
```bash
cgw status      # expect: Doctor result: ready
grep tunnel_id ~/.codex-chatgpt-web/tunnel/profiles/codex-chatgpt-web.yaml     # must be the NEW id
tail -n 5 ~/Library/Application\ Support/tunnel-client/logs/codex-chatgpt-web.log | grep -o '"msg":"[^"]*"'
```
Expect "tunnel-client started" and no repeating `poll failed`. Old id in the yaml → run `cgw use <label>` again.

### 9. Hand back (two manual steps, guide them one by one)
1. `open "https://chatgpt.com/#settings/Plugins"` → *"Gắn tunnel mới vào connector 'Codex Native2' và refresh plugin Codex. Xong nhắn mình."*
2. *"Restart app Codex một lần để nạp lại danh sách model."*

Final report (short): launcher version, active label, tunnel id (never the key), doctor result, what's left for them (nothing if both manual steps are done).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Setup cancelled: acknowledgement was not provided` | Notice not accepted. Ask the user, then `CGW_ACK=1`. |
| `Cannot bind 127.0.0.1:17841` | Launcher's own `serve` holds the port. `cgw use` handles it. |
| `Launcher browser host is unavailable: descriptor is missing` | Launcher not running. Open it, wait for `~/.codex-chatgpt-web/runtime/launcher-browser.json`. |
| Log: `401 tunnel_active_organization_required` / 403 | Key from another org, or profile still on the old tunnel. Redo step 6; `cgw use <label>`. |
| `Tunnel service is not installed; rerun full setup` | Don't use `codex-chatgpt-web tunnel restart` (launcher owns the runtime). Use `cgw use <label>`. |
| `a ChatGPT login exists but no current account is registered` | `cgw adopt <label>` for the account logged in now. |
| `cgw: no codex-chatgpt-web version found` | Launcher never started; open it once. |
