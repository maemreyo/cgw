# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/), versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-07
### Added
- `cgw version`; warning when the installed codex-chatgpt-web differs from the tested release (`cgw status` shows both); README "Compatibility" section.
- `cgw clip tunnel|key NAME`: take the tunnel id / runtime key from the clipboard (key verified, stored 0600, clipboard cleared) so secrets never pass through chat or shell history.
### Changed
- `AGENT_SETUP.md` rewritten as a step-by-step guided conversation; the user only clicks, copies and confirms.

## [0.1.0] - 2026-10-07
### Added
- `cgw adopt | add | use | list | status | remove` for switching Codex Web GPT between ChatGPT accounts.
- `DRY=1` preview mode; `CGW_ACK=1` for non-interactive setup after the user accepted the unofficial-software notice.
- `AGENT_SETUP.md`: runbook so an AI agent can install the launcher and apply a new tunnel end to end.
