---
name: mcp-development
description: Standards and protocols for implementing and maintaining Navidrome MCP server tools and resources.
---

# MCP Development Standards

This skill defines the technical standards for the Navidrome MCP ecosystem.

## 1. Professional Logging (Local JSON)
We use a structured local JSON logging system. Do NOT use standard `print()` or basic `logging.info()`.
- **Implementation**: Use the `@log_execution` decorator for all tools.
- **Pattern**:
    - `logger.info("Message", extra={"key": "value"})`
    - Fields: `timestamp`, `level`, `name`, `message`, `tool`, `inputs`, `duration_ms`, `result_summary`.
- **Level**: Use `DEBUG` for verbose tech details, `INFO` for tool execution success, `ERROR` for failures with `exc_info=True`.

## 2. Safety & Validation
- **ID Validation**: All Navidrome IDs should be validated as 32-character hex strings where possible.
- **Fail Fast**: If a dependency (like Navidrome connection) is down, the tool should return a structured error JSON instead of crashing.
- **Fuzzy Fallback**: For search tools, if a strict search returns no results, implement a secondary "fuzzy" search or broader query before giving up.

## 3. Code-to-Doc Synchronization (CRITICAL)
Architectural decisions in documentation MUST be mirrored in the MCP server resources.
- If `docs/architecture/curator_manifesto.md` is updated, the `CURATOR_MANIFESTO_TEXT` constant in `src/navidrome_mcp_server.py` MUST be updated in the same task.
- Ensure `usage_guide()` prompt in code reflects all current tools available in the server.

## 4. Tool Protocol
- **Naming**: Use lowercase with underscores (e.g., `get_smart_candidates`).
- **Descriptions**: Must be clear and describe parameters accurately for LLM consumption.
- **Returns**: Always return a JSON-stringified object or list for structured parsing.

## 4. TDD Workflow
Every bug fix or new tool MUST follow this cycle:
1. Create a `tests/test_filename.py`.
2. Write a test that reproduces the bug or defines the desired behavior.
3. Verify the test fails.
4. Implement the fix/feature in `src/navidrome_mcp_server.py`.
5. Verify the test passes.

## 5. Discovery & Documentation
- **Manifesto**: New discovery logic should be mirrored in the `curator//manifesto` resource.
- **Handshake**: Ensure `navidrome://info` reflects any new capabilities added to the server.
- **README**: Public-facing changes must be documented in the root `README.md`.
