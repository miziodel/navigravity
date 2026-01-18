# NaviGravity Changelog

### v0.1.8 - Smart Selection (2026-01-18)

#### ✨ New Features
- **Smart Scoring Logic**: Implemented a point-based scoring system to improve track selection.
    - **Formula**: Neutral (3), Stars (+1 per star), Heart (+5).
- **Intelligent Selection**: `get_smart_candidates` now sorts results by `smart_score` (Descending) and shuffles the top tier to ensure both quality and discovery variety.

#### 🏗️ Fixes & Improvements
- **Smart Scoring Bug**: Fixed issue where low-rated tracks (1-2 stars) were not being penalized due to a metadata key mismatch (`userRating` vs `rating`).
- **Playlist Persistence**: Fixed "Race Condition" where creating large playlists (>20 tracks) resulted in partial saves. Implemented automatic batching (10 tracks/request) in `manage_playlist`.
- **Sync Ghost Bug**: Implemented mandatory ID verification in `manage_playlist` to prevent silent failures when updating playlists with stale or invalid track IDs.
- **Version Control**: Bumped project version to `0.1.8`.

#### 📝 Documentation
- **Curation Blueprints**: Introduced the "Blueprint" category for complex curation strategies. Added the first draft: [The Universal Bridge (A ➔ B)](../architecture/blueprints/universal_bridge_draft.md).

### Infrastructure & Governance Upgrades (2026-01-18)

#### 🏗️ Infrastructure & Rules
- **Project Identity**: Established the `Senior Methodical Engineer` persona in `.agent/rules/01-identity.md`.
- **MCP Standards**: Codified professional standards (logging, validation, TDD) in `.agent/skills/mcp-development/SKILL.md`.
- **Governance**: Implemented mandatory planning protocols and documentation integrity checks in `.agent/rules/05-planning-standard.md`.
- **Discovery Handshake**: Created `.agent/rules/02-handshake-discovery.md` to ensure server resources (Manifesto, Handshake) stay in sync with architecture docs.

#### 🔄 Workflows
- **Plan & Execute**: Standardized the dev lifecycle in `.agent/workflows/plan-and-execute.md`.
- **Session Cleanup**: Refined `.agent/workflows/cleanup-session.md` with strict isolation and staged-only commit protocols.

#### 📝 Project Metadata
- **Metadata Automation**: Updated `docs/metadata.json` and `docs/roadmap/prioritized_roadmap.md` to reflect current state.

### v0.1.7 - Stability & Discovery (2026-01-18)

#### ✨ New Features
- **Similarity Tools**: Added `get_similar_artists` and `get_similar_songs` for graph traversal and "Radio Mode".
- **Multi-Mode Harvesting**: `get_smart_candidates` now supports comma-separated modes for broad net gathering.
- **Rediscovery V2**: Implemented "Album Archeology" (mode=`rediscover`) shifting from random songs to random albums for better coherence.
- **Advanced Discovery Modes**: 
  - `rediscover_deep`: Iterative mining loop for high-dated tracks.
  - `fallen_pillars`: Discography deep-scan for top artists' forgotten tracks.
  - `similar_to_starred`: Proximity recommendations using favorites as seeds.
- **Multi-Genre Tools**: 
  - `search_by_tag`: intersection/union filtering for complex vibe searches.
  - `get_genre_tracks`: now accepts a list of genres for batched discovery.
- **Quality Gates**: 
  - `validate_playlist_rules`: new dry-run tool for diversity and mood verification.
- **Roadmap Strategy**: Consolidated roadmap strategy into `docs/roadmap/prioritized_roadmap.md`.

#### 🏗️ Fixes & Improvements
- **Strict Filtering**: `get_smart_candidates` now strictly excludes tracks with `bpm=0` when `min_bpm` is requested, returning an error if strict filtering matches 0 candidates (Fixing "Silent Mode" bug).
- **Graceful Quality Checks**: `assess_playlist_quality` now yields warnings instead of failing when encountering "Ghost IDs" (missing tracks).
- **Search Robustness**: Integrated `_fetch_search_results` abstraction for all search tools, providing automatic fuzzy fallback and response normalization.
- **Tiered Similarity**: `get_similar_artists` now follows a tiered lookup (Direct Similarity -> Bio Info -> Genre Fallback) for significantly higher hit rates in diverse libraries.
- **Improved ID Sanitization**: `assess_playlist_quality` now uses robust regex extraction to handle IDs embedded in Markdown links or with trailing noise.
- **Version Control**: Bumped project version to `0.1.7`.

---

### v0.1.6 - The "Curator" Protocol (2026-01-10)

#### 🎩 Curator Manifesto
- **Implicit Protocol**: Introduced the `Curator Manifesto` (Harvest -> Filter -> Execute), moving from "Librarian" to "Curator" mindset.
- **MCP Resource**: Exposed the manifesto via `curator://manifesto` for on-demand agentic introspection.
- **MCP Prompt**: Added `curator_mode` prompt to automatically inject the protocol into new session contexts.

#### 🏗️ Quality & Infrastructure
- **Test Alignment**: Re-aligned `tests/test_missing_music_tools.py` with the `analyze_library` unified API.
- **Git Hygiene**: Updated `.gitignore` to prevent documentation `updated_at` timestamps from triggering false-positive diffs during Agent edits.


---

### v0.1.5 - Precision Curation (2026-01-10)

#### 🛠️ Smart Candidate Enhancements
- **Advanced Filtering**: Integrated `include_genres`, `exclude_genres`, `min_bpm`, and `max_bpm` parameters into `get_smart_candidates`.
- **Inferred Moods**: Added `mood` parameter ('relax', 'energy', 'focus') that automatically maps to BPM and genre constraints.
- **Diversity Constraints**: Implemented `max_tracks_per_artist` to prevent artist dominance in generated lists.
- **Metadata Enrichment**: Track objects now include `bpm`, `userRating`, `comment`, and `path`.

#### 🛣️ Roadmap
- **Strategy Draft**: Archived the "MCP Server Improvements" implementation plan in `docs/roadmap/draft/mcp_server_improvements_plan.md` for future execution (Graceful Degradation, Similar Artists, Multi-Mode Harvesting, Batch Genre).

---

### v0.1.4 - Discoverability & Feature Gaps (2026-01-10)

#### ✨ New Features
- **Playlist Management**: Added `operation='delete'` to `manage_playlist` tool, enabling full lifecycle management of playlists.

#### 🔍 Discoverability
- **Root Resource**: Verified `navidrome://info` resource is correctly implemented and discoverable for agentic handshake.

---

### v0.1.3 - Living Documentation (2026-01-10)

#### 📚 Documentation Architecture
- **Living Documentation**: Migrated project documentation from `memory-bank/` to a structured `docs/` hierarchy.
  - **Structure**: Organized into `overview`, `architecture`, `roadmap`, and `artifacts`.
  - **Single Truth**: Established `docs/` as the canonical source for Agent knowledge.
  - **Integration**: Linked `docs/` directly to the Agent's global knowledge base via symlink.
  - **Rules**: Added strict agent rules (`.agent/rules/90_documentation.md`) for maintaining documentation.

#### 🏗️ Infrastructure & Quality
- **Modern Packaging**: Refactored project setup to use `pyproject.toml` for robust dependency and build management.
- **Logging Reliability**: Fixed issue where log directory creation would fail if using relative paths; now ensures directory existence before writing.
- **Test Suite**: Enhanced test assertions for stronger regression protection.

---

### v0.1.2 - The "Consolidation" Release (2026-01-05)

#### ♻️ Refactoring & Consolidation
- **Unified Analytics**: Consolidates `get_library_pillars`, `analyze_library_composition`, and `analyze_user_taste_profile` into a single powerful tool: `analyze_library(mode='pillars'|'composition'|'taste_profile')`.
- **Unified Curation**: Merges playlist creation and mood tagging into `manage_playlist(operation='create'|'append'|'get')`.
- **Streamlined Discovery**: Integrated divergent recommendations into `get_smart_candidates(mode='divergent')`.
- **Code Cleanliness**: Renamed generic internal variables (e.g., `searchResult3`) to be human-readable, decoupling logic from API specifics.

#### 🐛 Fixes
- **Search Reliability**: Fixed critical bug in `search_music_enriched` where nested `searchResult3 -> song` dictionaries were not parsed correctly, causing "unreliable results" errors.
- **Docstring Alignment**: Updated `manage_playlist` docstrings to strictly use the `NG:Mood:{MoodName}` convention.

#### 🧠 Agent Persona
- **Lateral Thinking**: Updated the "Curator Persona" to finding vibes across genres (e.g., Ambient in Jazz/Classical) to solve "rigid prompt" issues.

---

### v0.1.1 - Enhanced Analytics & Pillars (2026-01-05)

#### ✨ New Features
- **Library Pillars**: Implemented `get_library_pillars` to identify "Canonical" artists by Album Count, revealing the library's backbone (e.g., Classical/Italian Canon).
- **Inventory Analysis**: Implemented `analyze_library_composition` to map genre distribution by volume ("Cold Analysis").
- **Deep Scan**: Upgraded `get_smart_candidates(mode='lowest_rated')` to sample 2000+ items, enabling the discovery of rare low-rated tracks in large libraries.
- **Top 30+**: Enhanced statistical fetching to support larger result sets for "Heavy Hitters".

#### 🐛 Fixes & Improvements
- **Playlist Idempotency**: Updated `create_playlist` to detect and overwrite existing playlists by name, preventing duplicate clutter (e.g., "Playlist (1)").
- **Documentation**: Separated Roadmap and Changelog for better clarity.

---

### v0.1.0 - Foundation & Intelligent playlisting (2026-01-05)

#### ✨ New Features
- **Agentic Playlist Engines**:
  - `Must Listen (Unplayed)`: Smart discovery of unplayed tracks from starred albums with round-robin diversity.
- **Discovery Tools**:
  - `get_genres`: Lists all library genres with metadata counts.
  - `explore_genre`: Deep dive metrics for specific genres (Top Artists, Album counts).
  - `get_genre_tracks`: Rapid candidate mining by genre.
  - `get_smart_candidates(mode='unheard_favorites')`: New mode for starred-but-unplayed content.

#### 🐛 Fixes & Improvements
- **Libsonic Connection**: Fixed critical bug where `py-sonic` failed to parse full URLs. Implemented robust URL parsing in `navidrome_mcp_server.py`.
- **Quality Gates**: Implemented "Strict Mode" constraints (Max 3 tracks/artist, Min 30 unique artists) for all generated playlists.
- **Documentation**: Added `curation_patterns.md` and `llm_tool_usage.md` "Semantic Exploration" pattern.

### v0.0.2 - Infrastructure & Observability (2026-01-04)

#### 🛠️ Core Updates
- **Structured Logging**: Implemented JSON logging decorator for all tools to track duration, inputs, and errors.
- **Configuration**: Standardized `.env` loading for credentials.
- **Discovery**: Added `get_genre_tracks` basic implementation.

### v0.0.1 - Initial Release (2026-01-03)

#### 🎉 Initial Launch
- **Server**: Basic MCP server implementation using `FastMCP`.
- **Core Tools**:
  - `get_smart_candidates` (Rediscover, Hidden Gems).
  - `assess_playlist_quality` (Basic diversity check).
  - `create_playlist`.
  - `set_track_mood` (Virtual Tags).
- **Documentation**: Initial `README.md` and Project Manifest.
