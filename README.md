# cgw — account switcher for Codex Web GPT

[![lint](https://github.com/maemreyo/cgw/actions/workflows/lint.yml/badge.svg)](https://github.com/maemreyo/cgw/actions/workflows/lint.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) ![platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

`cgw` is a small Bash tool that moves a [codex-chatgpt-web](https://github.com/miuuyy/codex-chatgpt-web)
("Codex Web GPT" launcher) install from one ChatGPT account to another with a single command.
It saves and restores each account's ChatGPT sign-in, tunnel ID and runtime key, so you don't have to repeat the
full-harness setup by hand every time you change accounts (for example personal vs. work).

`cgw` activates **one account at a time, when you ask it to**. It does not rotate accounts automatically, pool them,
or work around usage limits.

> **Using an AI agent (Claude Code, Codex, …)?** Just send it:
> `Install and update a new tunnel for me: https://raw.githubusercontent.com/maemreyo/cgw/main/AGENT_SETUP.md`
> The agent walks you through it one step at a time ([AGENT_SETUP.md](AGENT_SETUP.md)); you only click, copy and confirm.

## Requirements

- macOS (developed on Apple silicon) with the Codex Web GPT launcher installed — tested with 6.1.5.
- `bash`, `python3`, `curl` (all ship with macOS).
- An OpenAI tunnel and a runtime key with **Tunnels Read + Use** for each account, created in that account's organization.

## Install

```bash
git clone https://github.com/maemreyo/cgw ~/Documents/projects/cgw
~/Documents/projects/cgw/install.sh      # symlinks cgw into ~/.local/bin
```

## Quick start

```bash
cgw adopt personal                       # register the account that is set up right now
cgw clip tunnel work                     # copy the tunnel ID in the OpenAI dashboard, then run this
cgw clip key work                        # copy the new runtime key, then run this (verified, stored 0600, clipboard cleared)
cgw use work                             # switch; the first time it opens a ChatGPT sign-in
cgw use personal                         # switch back, no sign-in needed
```

Prefer files over the clipboard? `cgw add NAME TUNNEL_ID KEY_FILE` does the same in one go.

## Commands

| Command | What it does |
|---|---|
| `cgw adopt NAME` | Register the account that is configured right now (do this once before the first switch). |
| `cgw add NAME TUNNEL_ID KEY_FILE` | Register or update an account; the key is validated against the API and copied with mode 0600. |
| `cgw clip tunnel NAME` | Read the tunnel ID from the clipboard. |
| `cgw clip key NAME` | Read the runtime key from the clipboard, verify it can read the tunnel, store it, clear the clipboard. |
| `cgw use NAME` | Switch to `NAME`. `DRY=1 cgw use NAME` previews every step; `CGW_ACK=1` accepts setup's notice non-interactively (see below). |
| `cgw list` / `cgw status` / `cgw remove NAME` | List accounts, run the launcher's `doctor`, delete a saved account. |

## What is per-account

| Piece | Where it lives | How cgw handles it |
|---|---|---|
| ChatGPT sign-in | `~/Library/Application Support/Codex Web GPT/Partitions/codex-web-gpt-chatgpt` (~360 MB) | moved to `~/.codex-chatgpt-web/accounts/<name>/partition` when switching away, moved back when switching in |
| Tunnel ID + runtime key | `accounts/<name>/account.env`, `accounts/<name>/runtime.key` | passed to `setup --full` |
| Connector "Codex Native2" attached to the tunnel | ChatGPT → Settings → Plugins | **manual, once per account** — it cannot be automated |

All account data stays under `~/.codex-chatgpt-web/accounts/` (mode 0700). Nothing secret is in this repository.

## What `cgw use` does, and why

1. Quit the launcher and any stray `tunnel-client run`.
2. Swap the ChatGPT partition (an account without a saved sign-in gets `setup --login`).
3. Open the launcher — `setup` needs its browser descriptor, `runtime/launcher-browser.json`.
4. Stop the launcher's own `serve` on port 17841 — `setup` binds that port itself and otherwise fails with `EADDRINUSE`.
5. Run `setup --full --refresh-account-capabilities --tunnel-id … --runtime-key-file …`.
6. Quit and reopen the launcher. It owns the tunnel runtime and only regenerates
   `tunnel/profiles/codex-chatgpt-web.yaml` at startup; skipping this leaves the old tunnel running
   (log: `401 tunnel_active_organization_required`).
7. Run `doctor`.

## Compatibility

`cgw` drives the launcher through its CLI and on-disk layout, not a stable API, so a new codex-chatgpt-web release can break it.
It relies on:

- CLI: `cli.js setup --full [--login] [--acknowledge-unofficial] [--refresh-account-capabilities] --tunnel-id … --runtime-key-file …`, `doctor`
- Files: `~/.codex-chatgpt-web/{config.json,versions/*,runtime/launcher-browser.json,secrets/,tunnel/profiles/}`
- Launcher behavior: owns `serve` on port 17841 and the tunnel runtime, regenerates the tunnel profile only at startup
- App data: the Electron partition `Partitions/codex-web-gpt-chatgpt` under `~/Library/Application Support/Codex Web GPT`

Last verified: **6.1.5**. `cgw` picks the newest installed version and prints a warning if it differs from the tested one.
After updating the launcher, run `DRY=1 cgw use NAME`, then `cgw use NAME` and `cgw status`; if something breaks, open an issue with
your launcher version and the failing step. Bump `TESTED_VERSION` in `cgw` when you verify a new release.

## Notes and gotchas

- `setup` requires accepting the launcher's "independent, unofficial software" notice. `cgw` never accepts it for you;
  `setup` prompts, or you opt in explicitly with `CGW_ACK=1 cgw use NAME` after reading it.
- A runtime key only works for tunnels in its own organization (401/403 otherwise).
- `codex-chatgpt-web tunnel restart` does not help ("Tunnel service is not installed") while the launcher owns the runtime.
- Updating the launcher: quit it, then
  `curl -fsSL https://github.com/miuuyy/codex-chatgpt-web/releases/latest/download/install-launcher.sh | sh`
  (checksum-verified; keeps your sign-in). A new version may show the notice again.

## Setting up a new machine

1. Install the launcher with the command above and open it once.
2. `git clone` this repository and run `./install.sh`.
3. For each account: create a tunnel and a runtime key at platform.openai.com → `cgw clip tunnel` / `cgw clip key` → `cgw use NAME` → sign in to ChatGPT → attach the connector.

Saved sign-ins are not portable between machines; sign in again on the new one.

## Known limitations

- macOS only; the launcher paths are hard-coded to its default locations.
- The partition swap between two real accounts is implemented but has had little real-world testing — try it with a throwaway account before relying on it.
- The ChatGPT connector step is manual.

## Disclaimer

Independent project, not affiliated with or endorsed by OpenAI or the codex-chatgpt-web authors. The underlying
launcher automates a ChatGPT web session and is unofficial software; you are responsible for complying with
OpenAI's terms. Use it only with accounts you own. No warranty — see [LICENSE](LICENSE).

## Contributing, security, license

[CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [CHANGELOG.md](CHANGELOG.md) · [MIT License](LICENSE)
