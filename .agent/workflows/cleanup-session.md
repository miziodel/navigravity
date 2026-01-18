---
description: Workflow to safely close a session by ensuring work from ONLY this session is preserved.
---

# Session Cleanup (Strict Protocol)

This workflow ensures work from the **current session** is safely committed and temporary artifacts are removed.

## 1. Documentation Integrity
- Verify that `roadmap`, `changelog`, and `metadata.json` have been updated to reflect **this session's** work.
- Ensure the `task.md` for this session is marked as completed.

## 2. Session Assessment
- Run `git status` to identify **Staged Changes** (the work to be committed).
- **CRITICAL**: Identify files changed in parallel by other agents/sessions and ensure they are **NOT** staged. 
- Distill any new patterns into the **Global Knowledge Base** if required.

## 3. The Proposal (STOP POINT 🛑)
- Present a concise plan:
    - **Staged for Commit**: (List files)
    - **Discard/Cleanup**: (List artifacts like task.md, implementation plans)
- **Action**: Call `notify_user` and wait for explicit confirmation.

## 4. Execution
- **Commit**: Run `git commit` for **STAGED files only**. The message must be specific to this session's work.
- **Cleanup**: Delete temporary files and session artifacts.

## 5. Handoff
- "Session work is clean and committed. Reusable knowledge is safe. You may delete this chat."
