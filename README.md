# cgw — account switcher for Codex Web GPT

Switches [codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web) ("Codex Web GPT" launcher,
tested with 6.1.5, macOS arm64) between ChatGPT accounts in one command, instead of redoing
the setup by hand each time.

> **AI agents:** follow [AGENT_SETUP.md](AGENT_SETUP.md) to install/update a tunnel end-to-end.

```
cgw adopt NAME                       register the account that is set up right now
cgw add NAME TUNNEL_ID KEY_FILE      register another account (key copied 0600, validated against the API)
cgw use NAME                         switch (DRY=1 cgw use NAME previews every step)
cgw list | status | remove NAME
```

## What is per-account

| Piece | Where it lives | How cgw handles it |
|---|---|---|
| ChatGPT login | `~/Library/Application Support/Codex Web GPT/Partitions/codex-web-gpt-chatgpt` (~360MB) | moved to `~/.codex-chatgpt-web/accounts/<name>/partition` when switching away, moved back when switching in |
| Tunnel id + runtime key (Tunnels Read+Use, from that account's OpenAI org) | `accounts/<name>/account.env`, `runtime.key` | passed to `setup --full` |
| Connector "Codex Native2" attached to the tunnel | ChatGPT → Settings → Plugins | **manual, once per account** (cannot be automated) |

All account data stays under `~/.codex-chatgpt-web/accounts/` (mode 700). Nothing secret is in this repo.

## `cgw use` sequence (and why)

1. Quit launcher, kill stray `tunnel-client run`.
2. Swap the ChatGPT partition (new account without a saved login → `setup --login`).
3. Open launcher (setup needs its browser descriptor `runtime/launcher-browser.json`).
4. Kill the launcher's own `serve` on :17841 — `setup` binds that port itself, else `EADDRINUSE`.
5. `setup --full --refresh-account-capabilities --tunnel-id … --runtime-key-file …`.
6. Quit + reopen launcher — the launcher owns the tunnel runtime and only regenerates
   `tunnel/profiles/codex-chatgpt-web.yaml` at startup; skipping this leaves the old tunnel
   running (401 `tunnel_active_organization_required`).
7. `doctor`.

## Gotchas learned

- `setup` requires accepting the "unofficial software" notice (`--acknowledge-unofficial`).
  cgw deliberately does **not** pass it; setup prompts when needed.
- A runtime key only works for tunnels in its own organization; the old account's key gets 403/401 on another org's tunnel.
- `codex-chatgpt-web tunnel restart` does not help ("Tunnel service is not installed") when the launcher owns the runtime.
- Updating the app: quit launcher, then
  `curl -fsSL https://github.com/miuuyy/codex-chatgpt-web/releases/latest/download/install-launcher.sh | sh`
  (checksum-verified). A new version may ask for the notice again.

## New machine

1. Install the launcher (command above) and open it once.
2. `./install.sh`
3. Per account: create a tunnel + runtime key at platform.openai.com → `cgw add NAME TUNNEL_ID KEY_FILE` → `cgw use NAME` → sign in to ChatGPT → attach the connector.
Login snapshots are not portable across machines; sign in again on the new one.

## Status

`adopt/add/list` and the `DRY=1` flow are verified. The live partition swap between two real accounts
had not been exercised when this was written — test with a throwaway account first.
