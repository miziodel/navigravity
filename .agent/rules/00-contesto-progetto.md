---
trigger: always_on
priority: 00
---

# Context: NaviGravity Workspace

## Startup Reads (mandatory)

Before starting any task in this workspace, read the following files in order:

- `README.md` — project overview, available tools, setup instructions
- `.brainos/context-map.md` — **project state, critical gotchas, and agent cheat-sheet** (updated each session)
- `docs/overview/llm_tool_usage.md` — how the LLM must use the Curator tools
- `docs/overview/project_manifest.md` — project vision and philosophy

## What This Project Is

**NaviGravity** is a Python MCP server bridging a Navidrome music library to an LLM agent. It implements the **Curator Manifesto**: a quality-first curation pipeline (Harvest → Filter → Execute) with strict diversity gates.

## Quick Reference

| Need | Go To |
|------|-------|
| Architecture overview | `docs/architecture/mcp_architecture.md` |
| Tool API reference | `docs/architecture/api_schema.md` |
| Curation recipes | `docs/overview/curation_patterns.md` |
| Past decisions | `.brainos/decisions.jsonl` |
| Roadmap | `docs/roadmap/roadmap.md` |
| Version history | `docs/roadmap/changelog.md` |

> See `.brainos/context-map.md` for the full key-files table, decision history, and critical gotchas.
