# 2026 Q1 Roadmap: Consolidation & Evolution

This document consolidates the drafts found in `docs/roadmap/draft/` into a single prioritized execution strategy.

**Source Documents:**
1. `mcp_black_box_feedback.md` (Critical Fixes)
2. `mcp_server_improvements_plan.md` (Infrastructure & Tools)
3. `monograph_manifesto.md` (Advanced Product Feature)

---

## 📅 Roadmap Overview

### Phase 1: Stability & Foundation (v0.1.7)
**Goal:** Restore trust in the agent's basic operations. Fix "silent failures" and "ghost IDs".
**Priority:** 🔴 CRITICAL (Immediate)

*   **ID Persistence & Graceful Degradation**
    *   *Ref:* `mcp_black_box_feedback.md` (Item 1)
    *   Action: Implement `assess_playlist_quality` robust retry logic and skip-on-missing instead of crash-on-missing.
*   **Strict Parameter Handling (Fail Fast)**
    *   *Ref:* `mcp_black_box_feedback.md` (Item 2)
    *   Action: If `mode='top_rated'` doesn't support `mood` filtering, return a specific error/warning to the agent rather than silently ignoring the filter.
*   **Search Reliability**
    *   *Ref:* `mcp_black_box_feedback.md` (Item 3) + `mcp_server_improvements_plan.md`
    *   Action: Abstraction layer for search; if strict search fails, try fuzzy or fall back to broader terms.

### Phase 2: Enhanced Toolset (v0.1.7 Extension)
**Goal:** Empower the agent with efficient batch tools and cleaner abstractions.
**Priority:** 🟡 HIGH (Follow-up to Fixes)

*   **Batch Operations**
    *   *Ref:* `mcp_server_improvements_plan.md`
    *   Action: `batch_check_presence`, `search_by_tag`.
*   **Discovery Engine Expansion**
    *   *Ref:* `mcp_server_improvements_plan.md`
    *   Action: `similar_tracks_by_fingerprint`, `get_similar_artists`.
    *   Action: Rediscovery modes (`fallen_pillars`, `album_archeology`).

### Phase 3: "The Perfect Monograph" (v0.1.8)
**Goal:** High-level curation tailored to specific user "recipes".
**Priority:** 🔵 STRATEGIC (Next Feature)

*   **Monograph Curator Tool**
    *   *Ref:* `monograph_manifesto.md`
    *   Action: Implement `create_monograph_playlist` tool.
    *   Action: Implement "Wave" sorting logic (BPM/Intensity flow).
    *   Action: Implement "Mix Ratio" logic (Milestones vs Pearls vs Surprises).

---

## 🚀 Proposal: The Next Immediate Step

**Execute the "v0.1.7 Unified Plan"** (Phase 1 & 2 combined).

The `mcp_server_improvements_plan.md` is technically ready but needs to explicitly prioritize the *Stability Fixes* from the Black Box Feedback.

**Action Item:**
1.  Promote `mcp_server_improvements_plan.md` to `docs/roadmap/active/v0.1.7_plan.md`.
2.  Update it to explicitly list the *Black Box* fixes as blocking requirements for the release.
3.  Begin implementation of **v0.1.7**, starting with the **ID Persistence** fix (the most critical blocker).
