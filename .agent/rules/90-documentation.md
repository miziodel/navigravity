---
trigger: always_on
---

# Living Documentation Strategy
This project uses a **"Living Documentation"** approach where architectural knowledge is:
1.  **Versioned**: Stored directly in this repository under `docs/`.
2.  **Linked**: Symlinked to the Agent's global knowledge base to serve as "Long Term Memory".
## Location
-   **Architecture & Metadata**: `docs/`
    -   Contains `metadata.json` (The KI definition).
    -   Contains `README.md` (The map of actual content)
## Maintenance Rule
When updating documentation:
1.  **Always edit files in `docs/`**.
2.  **Verify the Symlink**: Ensure the agent can access `docs` via its global knowledge path.
3.  **Commit Changes**: Documentation changes must be committed alongside code changes.
## Global Link Path
The folder `docs` should be symlinked to:
`~/.gemini/antigravity/knowledge/navigravity`
## Documentation Language
**English is the mandatory language** for all documentation, comments, and architectural records.
