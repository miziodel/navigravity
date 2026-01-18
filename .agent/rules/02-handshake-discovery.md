---
trigger: always_on
---

# Handshake & Discovery Discovery Handshake Protocol

This rule ensures that the client-facing capabilities of the Navidrome MCP server are always accurate and discoverable.

## 1. Discovery Resources
The following resources MUST be kept in sync with the project's state:
- **`navidrome://info`**: Must reflect the current `__version__` and available capability categories.
- **`usage_guide` (Prompt)**: Must provide an accurate "Instruction Manual" for all implemented tools.
- **`curator//manifesto`**: Must be an exact copy or a faithful distillation of the latest `docs/architecture/curator_manifesto.md`.

## 2. Automatic Updates
Any change to the **public surface** of the server (new tools, modified parameters, changed curation philosophy) MUST trigger an update to these resources in the same PR/Task.

## 3. Client Guidance
Always prefer guiding the user to use the discovery tools (`get_server_info`, `usage_guide`) rather than hardcoding instructions in the chat, ensuring the "Source of Truth" remains the server itself.
