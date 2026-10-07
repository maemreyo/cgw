# Agent runbook: install / update a Codex Web GPT tunnel with `cgw`

You are an AI agent. The user sent you this file with a request such as
"install and update the new tunnel for me". Follow this runbook top to bottom.
Target: macOS, [codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web) ("Codex Web GPT" launcher).

## Ground rules (read first)

- **Never ask the user to paste a runtime key or token into chat, and never echo one.**
  Keys live in files; refer to them by path. Redact anything that looks like `sk-…` in output you show.
- **Do not create OpenAI accounts, API keys or tunnels yourself.** The user creates them in the
  platform UI; you only consume the tunnel id and a key *file*.
- `setup` shows an "independent, unofficial software … automates your ChatGPT web session" notice.
  **Ask the user to accept it explicitly in chat.** Only after a clear yes, run with `CGW_ACK=1`.
  A yes given for an earlier run does not carry over to a new version/run — ask again if setup prompts again.
- Do not delete `~/.codex-chatgpt-web/accounts/` or `~/Library/Application Support/Codex Web GPT/` (saved logins).
- `cgw use` quits and reopens the launcher and restarts the tunnel (~1 min). Tell the user first if a
  Codex turn might be running.

## 0. What to collect from the user

| Need | Where the user gets it |
|---|---|
| Account label (e.g. `work`) | their choice |
| Tunnel id `tunnel_<32 hex>` | https://platform.openai.com/settings/organization/tunnels (copy button — screenshots are easy to misread; ask for the text) |
| Runtime key **file path** (Tunnels Read+Use, created in the **same org/workspace as the tunnel**) | https://platform.openai.com/settings/organization/api-keys. Give the user this to run themselves: `umask 077; printf '%s' 'PASTE_KEY' > ~/.codex-chatgpt-web/secrets/<label>.key` |

If the tunnel id or key file is missing, stop and ask — do not guess.

## 1. Preflight

```bash
ls /Applications/"Codex Web GPT.app" ~/.codex-chatgpt-web/versions   # launcher installed?
which cgw || echo "cgw missing"
cgw list 2>/dev/null                                                  # registered accounts, * = active
```

## 2. Install the launcher (only if missing) or update it

1. `osascript -e 'tell application "Codex Web GPT" to quit'` and wait until `pgrep -x "Codex Web GPT"` is empty.
2. Read, then run the official installer (verifies SHA-256, replaces only the .app, keeps logins):
   ```bash
   curl -fsSL https://github.com/miuuyy/codex-chatgpt-web/releases/latest/download/install-launcher.sh -o /tmp/install-launcher.sh
   less /tmp/install-launcher.sh   # skim it; then:
   sh /tmp/install-launcher.sh
   ```
3. Confirm `~/.codex-chatgpt-web/versions/<new>/` exists (the launcher unpacks it on first start).

## 3. Install cgw (only if missing)

```bash
git clone https://github.com/maemreyo/cgw ~/Documents/projects/cgw && ~/Documents/projects/cgw/install.sh
```
Make sure `~/.local/bin` is on PATH.

## 4. Register / replace the tunnel

- **First time on this machine and a tunnel is already running** (`cgw list` empty, `~/.codex-chatgpt-web/config.json` exists):
  `cgw adopt <current-label>` so the existing login is not lost, *then* continue.
- **New account**: `cgw add <label> <tunnel_id> <key_file>`
- **New tunnel for an existing account** (same command, overwrites id + key, keeps the saved login):
  `cgw add <label> <new_tunnel_id> <key_file>`

`cgw add` validates the key against `GET /v1/tunnels/<id>`; HTTP 200 is required. If it fails with 401/403 the key
belongs to a different org/workspace than the tunnel — ask the user for a key created in the tunnel's org.

## 5. Apply

Ask for the notice acceptance (ground rules), then:

```bash
CGW_ACK=1 cgw use <label>      # preview first with: DRY=1 CGW_ACK=1 cgw use <label>
```

- If the label has no saved login, the launcher shows a ChatGPT sign-in. **Tell the user to sign in in that
  window and wait** — you cannot do it for them. Re-run `cgw use <label>` if setup timed out.
- Run it in a terminal that tolerates ~2 min; do not interrupt midway. If interrupted, just re-run `cgw use <label>`.

## 6. Verify (all must hold)

```bash
cgw status                                   # doctor: expect "Doctor result: ready"
grep -E 'tunnel_id' ~/.codex-chatgpt-web/tunnel/profiles/codex-chatgpt-web.yaml   # must be the NEW id
tail -n 5 ~/Library/Application\ Support/tunnel-client/logs/codex-chatgpt-web.log | grep -o '"msg":"[^"]*"'
```
Expect "tunnel-client started" and **no** repeating `poll failed`. The yaml showing the old id means the launcher
was not restarted — run `cgw use <label>` again.

## 7. Hand back to the user (manual, cannot be automated)

1. https://chatgpt.com/#settings/Plugins → attach the tunnel to connector **"Codex Native2"** and refresh the Codex plugin.
2. Restart the Codex app once.

Report: version installed, active label, tunnel id (not the key), doctor result, and the two manual steps.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Setup cancelled: acknowledgement was not provided` | You skipped the notice. Ask the user, then `CGW_ACK=1`. |
| `Cannot bind 127.0.0.1:17841` | Launcher's own `serve` holds the port. `cgw use` handles it; manual: quit launcher or kill that PID. |
| `Launcher browser host is unavailable: descriptor is missing` | Launcher not running. Open it, wait for `~/.codex-chatgpt-web/runtime/launcher-browser.json`. |
| Log: `401 tunnel_active_organization_required` / 403 on tunnel | Key from another org, or profile still on old tunnel. Fix key; re-run `cgw use`. |
| `Tunnel service is not installed; rerun full setup` | Don't use `codex-chatgpt-web tunnel restart`; the launcher owns the runtime. Use `cgw use <label>`. |
| `a ChatGPT login exists but no current account is registered` | Run `cgw adopt <label>` for the account that is logged in now. |
| `cgw: no codex-chatgpt-web version found` | Launcher never started; open it once. |
