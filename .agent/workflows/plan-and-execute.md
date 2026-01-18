---
description: Standard development workflow ensuring quality and documentation integrity.
---

# Development Lifecycle: Plan & Execute

Follow these steps for every coding task to ensure "Quality First" standards.

## 1. Context & Discovery
- Use `grep_search` and `view_file` to understand the current implementation.
- Read `docs/architecture` to align with existing patterns.

## 2. Technical Planning (STOP POINT)
- Create or update `implementation_plan.md`.
- **Requirements**:
    - Define clear **Goals**.
    - Explicit **TDD Plan** (List failing test cases).
    - **Documentation Impact** (Internal technical + Public README/Manifesto).
- Call `notify_user` with the plan and wait for approval.

## 3. TDD First (EXECUTION)
- Create the test file (e.g., `tests/test_feature.py`).
- Implement failing tests that match the plan.
- Run tests and verify failure (e.g., `pytest tests/test_feature.py`).

## 4. Implementation
- Write the minimum code required to pass the tests.
- Follow the protocols in the `mcp-development` skill (logging, safety, validation).

## 5. Verification & Documentation
- Run the full test suite to ensure no regressions.
- **Internal**: Update `docs/architecture` or `docs/overview` as planned.
- **Public**:
    - Update the project `README.md` if user/client interactions changed.
    - Update `curator//manifesto` and other server resources in `src/navidrome_mcp_server.py` to match architecture docs.
    - Update `docs/metadata.json` timestamps and artifacts.
- Create `walkthrough.md` to demonstrate the result.
