---
trigger: always_on
---

# Development Planning Standards

To ensure stability and documentation integrity, all development must follow the "Quality First" planning protocol.

## 1. Mandatory Planning Phase
Before writing any code (except for exploration/discovery), you MUST create or update an `implementation_plan.md` artifact.

### Implementation Plan Requirements:
- **Goals**: Clear description of the objective.
- **TDD Plan**: List of specific test cases to be written BEFORE implementation.
- **Documentation Impact**:
    - **Internal**: List of files in `docs/architecture` or `docs/overview` to be updated.
    - **Public**: Assessment of impact on `README.md` and `curator//manifesto`.
    - **Metadata**: Mandatory update of `docs/metadata.json` if documentation structure or artifacts change.
- **User Review**: Request approval via `notify_user` before proceeding to execution.

## 2. The TDD-First Rule
**Implementation starts with tests.**
- In every execution phase, the first tool call for code modification must be preceded or accompanied by the creation/execution of a failing test.
- No feature is considered "done" until verified by a passing test.

## 3. Documentation Governance
Documentation is not an afterthought; it is a deliverable.
- **Internal Docs**: Keep the technical blueprints updated.
- **Public README**: Update for any feature that changes how the user or a client interacts with the server.
- **Discovery Layer**: Ensure the server's self-description (manifesto, info resource) is accurate.

## 4. Mode Enforcement
- **PLANNING**: For research, design, and plan approval.
- **EXECUTION**: For TDD and implementation.
- **VERIFICATION**: For testing and finalizing documentation.
