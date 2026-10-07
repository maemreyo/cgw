# Agent runbook: install / update a Codex Web GPT tunnel with `cgw`

You are an AI agent. The user sent you this file with a request such as "install and update the new tunnel".
**Run this as a guided conversation: one step at a time, in the user's language** (the quoted lines below are English templates; translate them). The user must not need to
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
Note the launcher version; `cgw` prints a warning when it differs from the version it was tested with — relay that warning to the user, and if `setup` then fails on an unknown flag or missing file, stop and report instead of improvising. Decide silently which of steps 2–3 are needed. Tell the user one line: what's installed and what you'll do.

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
If `cgw list` is empty but `~/.codex-chatgpt-web/config.json` exists, ask: "Which ChatGPT account is set up on this machine right now, and what should I call it?" then
`cgw adopt <name>` — otherwise the current ChatGPT login would be lost on the first switch.

### 4. Which account? (ask)
Show `cgw list` and ask: update the tunnel of an existing account, or add a new account? Get a short label.
For a new label also ask: "Is this ChatGPT account already signed in inside the launcher?" (it will be asked to sign in during step 7 anyway).

### 5. Tunnel id — user copies, you read
1. `open "https://platform.openai.com/settings/organization/tunnels"`
2. Tell the user: *"Select the right organization for this account (top-left), create a tunnel if there isn't one yet (Create), then click the copy icon next to the `tunnel_…` ID and tell me 'done'."*
3. After "done": `cgw clip tunnel <label>` → prints the id. Show it back and ask "Is this the right tunnel?" (the name column is visible to them).
If it fails with "clipboard does not hold a tunnel id", ask them to click copy again.

### 6. Runtime key — user creates + copies, you read
1. `open "https://platform.openai.com/settings/organization/api-keys"`
2. Tell the user, concisely: *"Use the same organization and workspace as the tunnel. Create new secret key → name it (e.g. `codex-tunnel`) → permissions Restricted: **Tunnels = Read + Use** → Create. Copy the key (⌘C) and tell me 'done'. Do not paste it into the chat."*
3. After "done": `cgw clip key <label>`.
   - `verified (HTTP 200)` → continue.
   - `HTTP 401/403` → key is from another org/workspace or lacks permission. Explain, tell them to create another, repeat.
   - "does not look like a runtime key" → they copied something else; ask to copy again right after creation (keys are shown once).

### 7. Apply
Say what will happen (launcher closes/reopens, ~2 min) and show the notice from "Ground rules"; ask for the yes. Then:
```bash
CGW_ACK=1 cgw use <label>          # DRY=1 CGW_ACK=1 cgw use <label> previews
```
- No saved login for this label → the launcher opens a ChatGPT sign-in. Tell the user: *"Sign in to ChatGPT in the Codex Web GPT window that just opened, then tell me when you're done."* Wait. If setup timed out, re-run `cgw use <label>` (safe to repeat).
- Do not interrupt midway; re-running recovers.

### 8. Verify
```bash
cgw status      # expect: Doctor result: ready
grep tunnel_id ~/.codex-chatgpt-web/tunnel/profiles/codex-chatgpt-web.yaml     # must be the NEW id
tail -n 5 ~/Library/Application\ Support/tunnel-client/logs/codex-chatgpt-web.log | grep -o '"msg":"[^"]*"'
```
Expect "tunnel-client started" and no repeating `poll failed`. Old id in the yaml → run `cgw use <label>` again.

### 9. Hand back (two manual steps, guide them one by one)
1. `open "https://chatgpt.com/#settings/Plugins"` → *"Attach the new tunnel to the 'Codex Native2' connector and refresh the Codex plugin, then tell me when you're done."*
2. *"Restart the Codex app once so it reloads the model list."*

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
