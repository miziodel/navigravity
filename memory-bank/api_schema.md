# Navidrome MCP Tools Definition

This schema defines the tools available to the Antigravity Agent.

## 🧠 Analysis & Stats (Unified)

### `analyze_library`

**Purpose**: The central tool for understanding the library's content and user habits.

**Arguments**:
- `mode` (string):
    - `"composition"`: Returns genre distribution and total stats (Cold Analysis). Use this to see *what* is in the library.
    - `"pillars"`: Identifies core artists by Album Count (Canonical Analysis). Use this to find the "backbone" of the collection.
    - `"taste_profile"`: Analyzes recent/frequent/starred for top artists & eras (Warm Analysis). Use this to model the user's preferences.

**Returns**: JSON structure varying by mode.

### `batch_check_library_presence`

**Purpose**: Verification tool to find gaps (Missing Music) in bulk.

**Arguments**:
- `query` (List[Dict]): `[{"artist": "Name", "album": "Title"}, ...]`

## 🔍 Discovery & Search

### `get_smart_candidates`

**Purpose**: Statistical discovery logic (The "Magic List" engine).

**Arguments**:
- `mode` (string):
    - `"rediscover"`: High play count, not played in > 1 year.
    - `"forgotten_favorites"`: Starred/High rated, not played in > 6 months.
    - `"hidden_gems"`: Play count is 0 (Library-wide).
    - `"unheard_favorites"`: Play count is 0 (From Starred Albums).
    - `"recently_added"`: Newest albums.
    - `"most_played"`: Top tracks from frequent albums.
    - `"lowest_rated"`: Tracks with 1-2 stars (Deep Scan).
    - `"divergent"`: Tracks from genres rarely listened to (Breaks filter bubble).
- `limit` (int, default=50).

### `search_music_enriched`

**Purpose**: Keyword search with technical metadata.

**Arguments**:
- `query` (string).
- `limit` (int, default=20).

### `get_genres` / `explore_genre` / `get_genre_tracks`

**Purpose**: Standard genre-based exploration.

## 🎧 Curation & Management (Unified)

### `manage_playlist`

**Purpose**: Universal tool for creating, updating, and retrieving playlists and mood tags.

**Arguments**:
- `name` (string): Playlist name.
    - **Convention**: For virtual mood tags, use `NG:Mood:{MoodName}` (e.g., `NG:Mood:Focus`).
- `operation` (string):
    - `"create"`: Replaces or creates a playlist with the given tracks.
    - `"append"`: Adds tracks to an existing playlist (or creates it).
    - `"get"`: Returns the tracks in a playlist (random shuffled subset).
- `track_ids` (List[str]): Required for `create` and `append`.

### `assess_playlist_quality`

**Purpose**: (The "Bliss" Logic) Analyzes a list of candidate Song IDs for diversity. **MANDATORY** check before creation.

**Arguments**:
- `song_ids` (List[string]).

**Returns**: JSON with `diversity_score` and repetition warnings.