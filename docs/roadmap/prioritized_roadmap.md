# Prioritized Roadmap

## 🚨 CRITICAL / IMMEDIATE
- [x] **[META] Antigravity Configuration Improvements** (Done - v0.1.8)
- [x] **Smart Scoring Implementation** (Done - v0.1.8)

## 🔴 Priority 1 (Next Release: v0.1.9)
- [ ] **Server-Side Rating Filters**
    - Add `min_rating`, `max_rating` to `get_smart_candidates`
    - **Why**: Reduce token waste from client-side filtering (identified in `mcp_client_feedback.md`)
- [ ] **Batch Operations**
    - Implement `batch_search` to reduce N+1 calls
    - Complete `batch_check_presence` (currently partial)
    - **Why**: Performance for multi-artist workflows

## 🟡 Priority 2
- [ ] **Smart Favorite Albums Metric**
    - Implement "starred OR contains starred track" logic
    - **Why**: Improve taste profile accuracy (see `smart_favorite_metrics.md`)
- [ ] **Playlist Deduplication**
    - Add `ensure_unique` flag to `manage_playlist`
    - **Why**: Reduce client complexity

## 🟢 Priority 3 (Long-term)
- [ ] **Remote Access (SSE)**
    - Enable remote client connections
- [ ] **Advanced Search Filters**
    - Role filtering (composer vs performer)
    - Boolean logic syntax
- [ ] **Performance Optimization**
    - Caching for heavy queries
