# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - v0.1.7 (In Progress)

### Added
- **Similarity Tools**: Added `get_similar_artists` and `get_similar_songs` wrappers for graph traversal and "Radio Mode".
- **Roadmap**: Added prioritized roadmap and v0.1.7 active plan.

### Changed
- **Strict Filtering**: `get_smart_candidates` now strictly excludes tracks with `bpm=0` when `min_bpm` is requested, returning an error if strict filtering matches 0 candidates (Fixing "Silent Mode" bug).
- **Quality Assessment**: `assess_playlist_quality` now gracefully handles "Song not found" errors by skipping them and returning a `warnings` field instead of crashing (Fixing "Ghost ID" bug).
- **Search Reliability**: `search_music_enriched` automatically retries with a simplified query if strict search fails (Fixing "Fuzzy Search" issue).

### Fixed
- **BPM Loophole**: Closed logic gap where tracks with unknown BPM were included in mood-specific requests.
