# Security

`cgw` stores per-account runtime keys (mode 0600) and ChatGPT browser sessions under `~/.codex-chatgpt-web/accounts/` (mode 0700). Treat that folder like a password store.

Report vulnerabilities privately via GitHub **Security → Report a vulnerability** on this repo, not in public issues. If you leaked a runtime key, revoke it at https://platform.openai.com/settings/organization/api-keys first.
