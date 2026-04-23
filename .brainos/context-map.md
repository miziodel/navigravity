# NaviGravity — Agent Context Map

## Project Identity

NaviGravity (NG) is an open-source MCP (Model Context Protocol) server written in Python that exposes a self-hosted [Navidrome](https://www.navidrome.org/) music library as a set of intelligent tools for an LLM curator agent. The system is built around the **Curator Manifesto**: a strict quality-first pipeline (Harvest → Filter → Execute) that prevents lazy playlist generation and enforces diversity via the "Bliss Quality Gate."

## Current State

- **Version**: v0.1.9 (Preview/Beta)
- **Active milestone**: Agentic UX Refinement — `list_playlists`, similarity seeding, relaxed search matching shipped
- **Next milestone**: See `docs/roadmap/roadmap.md` — likely get_similar_tracks improvement and advanced scoring
- **BrainOS bootstrap**: Performed 2026-04-21 (Minimal Bootstrap — this session)

## Key Files

| File | Purpose |
|------|---------|
| `src/navidrome_mcp_server.py` | Single-file MCP server — all tools live here |
| `docs/overview/project_manifest.md` | Project vision, philosophy, workflow |
| `docs/overview/llm_tool_usage.md` | **Curator Manifesto** — how the LLM must use tools (read this!) |
| `docs/overview/curation_patterns.md` | Advanced playlist recipes (BPM zoning, round-robin diversity) |
| `docs/architecture/mcp_architecture.md` | MCP system architecture (stdio vs SSE, 3-actor diagram) |
| `docs/architecture/curator_manifesto.md` | Compact manifesto protocol (also served via `curator://manifesto` resource) |
| `docs/architecture/api_schema.md` | Tool & resource API definitions |
| `docs/roadmap/changelog.md` | Full version history |
| `docs/roadmap/roadmap.md` | Feature backlog |
| `docs/metadata.json` | KI-style metadata (symlinked into Antigravity knowledge base) |
| `.agent/rules/01-identity.md` | Senior Methodical Engineer persona |
| `.agent/rules/02-handshake-discovery.md` | Discovery resource sync protocol |
| `.agent/rules/05-planning-standard.md` | Mandatory plan-before-code protocol |
| `.agent/rules/90-documentation.md` | Living documentation strategy |
| `.agent/skills/mcp-development/SKILL.md` | Workspace-local MCP development standards |
| `tests/` | pytest test suite (mock-first, no live Navidrome required) |
| `pyproject.toml` | Modern packaging config |

## Decisions Log

_See `.brainos/decisions.jsonl` for structured ADRs_

Key past decisions (highlights):
- **Non-invasive moods**: Moods stored as playlists (`NG:Mood:{Name}`), never tag files directly
- **Stdio transport**: Chosen over SSE for local dev (zero network config, secure)
- **Multi-mode tool consolidation**: `analyze_library(mode=...)` over 3 separate tools (v0.1.2)
- **TDD protocol**: All new features start with failing tests; `pytest-mock` for Subsonic mocking
- **Smart Scoring**: `smart_score = Neutral(3) + Stars(+1) + Heart(+5)` for track ranking (v0.1.8)

## Agent Cheat Sheet

> ⚠️ **Critical gotchas for the next agent:**

1. **libsonic URL quirk**: `libsonic.Connection()` requires URL and port as **separate parameters** — never pass a full URL including port in the base URL field. (See `navigravity_debugging` KI)

2. **Subsonic API quirk**: `getAlbumList2` uses named argument `ltype=`, not `type=`. Getting this wrong causes silent empty results.

3. **Playlist race condition**: Creating playlists >20 tracks must use automatic batching (10 tracks/request) — `manage_playlist` handles this, but don't bypass it.

4. **Smart ID Sanitization**: `assess_playlist_quality` strips Markdown-embedded IDs (quotes/backticks) before calling the API — this prevents "Ghost ID" failures.

5. **TDD-first is mandatory** (`.agent/rules/05-planning-standard.md`): Write the failing test BEFORE implementation. No exceptions.

6. **Discovery resources must stay in sync**: Any change to public tool surface requires updating `navidrome://info`, `usage_guide` prompt, and `curator://manifesto` (Rule `02-handshake-discovery`).

7. **`docs/` is the single source of truth** — symlinked to Antigravity knowledge base. Always edit in `docs/`, never copy.

8. **`.agent/rules/` has no Rule 00** — there is no `00_contesto_progetto.md` yet. Add one if needed for cross-session continuity.
