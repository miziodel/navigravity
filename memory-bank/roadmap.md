# NaviGravity Roadmap & Changelog

## 🗺️ Roadmap (Backlog)

### 🔴 High Priority (Next Session)
- **Proactive Suggestions**: 
  - Goal: Identify "Missing Music" – artists or albums the user *should* have based on their taste but doesn't.
  - Implementation: Likely requires external API integration (Last.fm? MusicBrainz? Spotify?) to find "Similar Artists" not in DB.

### 🟡 Medium Priority
- **Sonic Flow Refinement**: Improve `get_sonic_flow` to handle "Era" transitions better (e.g., 70s -> 80s bridge).
- **"Album of the Day"**: A notification-based feature to suggest one forgotten masterpiece each morning.

---

## 📜 Changelog

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
