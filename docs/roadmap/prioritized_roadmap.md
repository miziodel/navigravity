# Prioritized Roadmap

## 🚨 CRITICAL / IMMEDIATE
- [x] **[META] Antigravity Configuration Improvements** (Done)
    - **Goal**: Automate "Living Documentation" and "Self-Publishing" checks via Agent Rules.
    - **Actions**:
        - Create `.agent/rules/05-planning-standard.md`.
        - Create `.agent/workflows/plan-and-execute.md`.
        - Update Skill definitions to enforce documentation updates.
    - **Why**: To ensure every future implementation plan automatically considers documentation integrity.

## 🔴 Priority 1 (v0.1.7-beta)
- [x] **Robustness & Reliability** (Done)
    - ID Santization in `assess_playlist_quality`.
    - Similarity Fallback in `get_similar_artists`.
    - TDD Enforcement.
- [x] **Ghost ID Handling** (Done)
- [x] **Missing Tool Verification** (Done)

## 🟡 Priority 2
- [ ] **Advanced Playlist Features**
    - "Divergent" mode refinement.
    - "Radio Mode" tuning.

## 🟢 Priority 3
- [ ] **Performance Optimization**
    - Caching for heavy queries.
