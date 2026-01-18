# NaviGravity Roadmap

## 🗺️ Roadmap (Backlog)

- **Remote Access (SSE)**: Implement Server-Sent Events (SSE) transport to allow remote clients to connect to NaviGravity (currently local stdio only).
- **Gap Analysis**: Automate the "Dual Identity" check to periodically suggest missing artists.

## 🔍 Features Pending Validation

These features have been identified in draft documents and require planning/implementation:

### Server-Side Enhancements
- **Rating Filters**: Add `min_rating`, `max_rating` parameters to `get_smart_candidates` and `search_music_enriched` for server-side filtering
- **Batch Operations**: 
  - `batch_search`: Accept array of queries to reduce N+1 calls
  - Complete `batch_check_presence` implementation (partially done)
- **Search Refinements**:
  - `role` filter (composer vs performer) in `search_music_enriched`
  - `in_library_only` flag for `get_similar_artists`
- **Similarity Enhancements**:
  - Seed sets (array support) for `get_similar_songs`
  - Ensemble Similarity logic (related formations treated as variants)

### Playlist Management
- **Deduplication**: `ensure_unique` flag for `manage_playlist` append operations
- **Pagination**: Cursor-based pagination for large result sets
- **Boolean Logic**: Structured filter syntax (e.g., `rating: {"gte": 4}`) instead of separate parameters

### Library Analysis
- **Smart Favorite Albums**: Metric for albums that are starred OR contain starred tracks
- **Semantic Exploration**: Enhanced taste profile with cultural context

### Validation Feedback (v0.1.8)
- **Search & Sensitivity**: Implement fuzzy or case-insensitive search (fix `eliminare!!` discovery issues).
- **Mood Strictness**: Add toggle to enforce strict BPM limits (e.g., for 'relax' mood).
- **UX Clarity**: 
  - Fix `lowest_rated` returning empty lists when results exist locally.
  - Add `smart_score_breakdown` to response for transparency (e.g., "+1 star, +5 heart").

**References**: See `docs/roadmap/draft/` for detailed specifications

## 🚀 Active Release: v0.1.8 (Smart Scoring)
**Status**: Released (2026-01-18)
**Changes**: [changelog.md](changelog.md)

### Delivered in v0.1.8
- **Smart Scoring**: Point-based scoring system (Neutral: 3, Stars: +1 per star, Heart: +5)
- **Intelligent Selection**: `get_smart_candidates` now sorts by `smart_score` and shuffles top tier for quality + variety

### Delivered in v0.1.7
- **Stability**: Graceful Quality Gates, Robust Search Fallback (`_fetch_search_results`), ID Sanitization
- **Tools**: `get_similar_artists`, `get_similar_songs`, `search_by_tag`, `validate_playlist_rules`
- **Discovery**: Multi-Mode Harvesting, Rediscovery V2 (Album Archeology)



## 🧠 Future Tool Enhancements

### 1. **"Album of the Day"**:

- **Concept**: A notification-based feature to suggest one forgotten masterpiece each morning.

### 2. Intelligent Artist Radio (`artist_radio`)
- **Concept**: Create a "Radio" experience mixed from the seed artist and similar artists.
- **Requirements**:
    - Need to aggressively cache `getSimilarArtists` results.
    - Algorithm should interleave "Hits" from the seed artist with "Top Tracks" from similar artists.
    - **Smart Mixing**: Don't just append lists. Shuffle similar artist tracks but keep seed artist tracks distributed evenly.

### 3. Sonic Flow (`get_sonic_flow`)
- **Concept**: Maintain a continuous "vibe" by matching BPM and Key.
- **Tech**:
    - `libsonic` supports `bpm` and `year` queries.
    - Need to implement a "Flow Logic":
        - `Target BPM = Seed BPM ± 10%`
        - `Target Year = Seed Year ± 5 years` (Optional, for "Era" flow)
    - **Challenge**: Many tracks in self-hosted libraries lack BPM metadata.
    - **Solution**: Fallback to Genre/Year if BPM is missing.

### 4. Advanced Mood Management
- Currently using `System:Mood:{Mood}` playlists.
- **Future**: Store mood data in custom ID3 tags or `comment` fields if Navidrome supports writing back to file.
- **Alternative**: Use a local SQLite DB sidecar to map `Effectiveness` of a track for a mood.

### 5. Monograph Curator (`create_monograph_playlist`)
- **Concept**: Agentic curation using "Golden Ratio" mixing (30% Hits, 50% Pearls, 20% Spice) and "Wave" sorting.
- **Spec**: [Monograph Manifesto](draft/monograph_manifesto.md) (includes "Hybrid Knowledge Injection" pattern).
