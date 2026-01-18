# MCP Client Feedback: Navigravity Integration

**Scope:** Observations from various curation sessions (Travel, Curator Mode).
**Perspective:** LLM Agent acting as a musical curator.

## 1. Technical Feedback - Session 2026-01-18 (The Curator Session)

### Discovery & Search
- **`search_music_enriched` (Strictness)**:
    - *Problem*: Searching for a performer (e.g. Keith Jarrett) returns many composers (Bach/Mozart).
    - *Requested Feature*: Add `role=composer|performer` or `strict_artist_match: boolean` to filter results.

### Similarity & Radio
- **`get_similar_artists` (Library Focus)**:
    - *Requested Feature*: Add `in_library_only: boolean` flag.
- **`get_similar_songs` (Seed Sets)**:
    - *Requested Feature*: Accept an array of `song_ids` for average-profile radio generation.

### Analysis & Quality
- **`assess_playlist_quality` (Ensemble Similarity)**:
    - *Observation*: Related formations (e.g. Jarrett Trio) are seen as distinct artists.
    - *Requested Feature*: Implement "Ensemble Similarity" logic.
- **Library Exploration (Favorite Albums)**:
    - *Requested Feature*: Consider an album "Favorite" if it is starred OR contains a starred track. (Drafted in `smart_favorite_metrics.md`).

## 3. Meta-Observation: Model Dynamics
- **Gemini 3 Pro (M7)**: High reasoning, prone to verbosity in tool calls (causing formatting loops).
- **Gemini 3 Flash (M18)**: Efficient, precise adherence to tool schemas.

The most significant inefficiency was the inability to filter by user metadata server-side.

*   **Issue:** I needed tracks with Rating >= 4 or Unrated.
*   **Current Workflow:** Call `get_smart_candidates` -> Receive 100 objects -> Client iterates and filters locally -> Discard 20% -> Request more to fill quota.
*   **Impact:** Wasted bandwidth/tokens retrieving track metadata that is immediately discarded.
*   **Recommendation:** Expose `min_rating`, `max_rating` (and potentially `exclude_rating`) directly in `get_smart_candidates` and `search_music_enriched`.

## 2. Lack of Batch Operations (N+1 Problem)

Targeted playlist creation often involves a specific list of artists.

*   **Issue:** User requested 5 specific Italian artists (Guccini, Bertoli, etc.).
*   **Current Workflow:** 5 separate sequential/parallel calls to `search_music_enriched` (`query="Guccini"`, `query="Bertoli"`...).
*   **Impact:** High latency, increased tool call overhead, potential rate-limiting.
*   **Recommendation:** Support array-based queries or a `batch_search` tool:
    ```json
    { "queries": ["Francesco Guccini", "Pierangelo Bertoli", "Whitemary"] }
    ```

## 3. Playlist Management "Blind Spots"

Managing a large playlist (300+ items) requires keeping state on the client side.

*   **Issue:** `manage_playlist(operation='append')` appears to be "dumb" (blind update). It does not natively handle deduplication.
*   **Current Workflow:** Client must get current playlist state -> Client maintains local set of IDs -> Client filters new candidates against local set -> Client sends append.
*   **Recommendation:** Add an `ensure_unique` (boolean) flag to `manage_playlist` operations, pushing the deduplication logic to the DB layer where it is cheaper.

## 4. Pagination & Diversity "Deep Paging"

Fetching a large diversified list (300 items) is difficult with a single endpoint.

*   **Issue:** `get_smart_candidates` with a high limit (e.g., 300) might time out or return truncated JSON due to context window limits.
*   **Current Workflow:** I had to manually "shard" my requests by Genre (`limit=40` for Rock, `limit=40` for Soul...) to build volume.
*   **Recommendation:**
    *   **Cursor-based pagination:** Allow robust fetching of large result sets in manageable chunks.
    *   **"Target Total" param:** Allow the server to handle the internal genre sharding if I just ask for "300 varied tracks".

## 5. Boolean Logic in Filtering

*   **Issue:** The exclusions are implicit text lists.
*   **Recommendation:** Explicit boolean logic for attributes would be clearer. E.g., `rating: { "gte": 4 }` or `bpm: { "gt": 90 }` rather than distinct named parameters which may or may not exist.
