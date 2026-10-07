# Contributing

Thanks for helping. `cgw` is a single Bash script; keep it that way (no extra runtime dependencies beyond macOS defaults, `python3`, `curl`).

- Run `bash -n cgw` and `shellcheck cgw` before opening a PR (CI does the same).
- Test with `DRY=1 ./cgw use NAME` first; changes to the account/partition swap need a manual test with **two real accounts** — say in the PR how you tested.
- Never commit keys, tunnel ids, org ids or ChatGPT session data. Redact logs.
- Update `README.md`, `AGENT_SETUP.md` and `CHANGELOG.md` when behavior changes. `AGENT_SETUP.md` is executed by AI agents — keep every command exact.
- Be kind; see the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) as our code of conduct.
