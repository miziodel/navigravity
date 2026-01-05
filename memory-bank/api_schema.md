# Navidrome MCP Tools Definition

This schema defines the tools available to the Antigravity Agent.

## 🧠 Discovery & Search Tools

### `get_genre_tracks`

**Purpose**: Fetches random tracks for a specific genre.

**Arguments**:

- `genre` (string).
- `limit` (int, default=100).

### `get_smart_candidates`

**Purpose**: Statistical discovery logic (The "Magic List" engine).

**Arguments**:

- `mode` (string):

    - `"rediscover"`: High play count, not played in > 1 year.
    - `"forgotten_favorites"`: Starred/High rated, not played in > 6 months.
    - `"hidden_gems"`: Play count is 0.
    - `"recently_added"`: Newest albums.

- `limit` (int, default=50): Number of tracks to return.

### `get_divergent_recommendations`

**Purpose**: Breaks the filter bubble. Finds genres the user never listens to.

**Arguments**:

- `limit` (int, default=20).

### `search_music_enriched`

**Purpose**: Keyword search with technical metadata.

**Arguments**:

- `query` (string).
- `limit` (int, default=20).

**Returns**: JSON with `bitrate`, `year`, `last_played`, `play_count`.

### `get_sonic_flow`

**Purpose**: Finds tracks that match the BPM or Era of a seed track.

**Arguments**:

- `seed_track_id` (string).
- `limit` (int, default=20).

### `artist_radio`

**Purpose**: Generates a mix based on an artist and their similar artists.

**Arguments**:

- `artist_name` (string).

## 🏷️ Mood & Tagging Tools (Virtual Tags)

### `set_track_mood`

**Purpose**: Tags a track with a mood by adding it to a System:Mood:{Name} playlist.

**Arguments**:

- `track_id` (string).
- `mood` (string).

### `get_tracks_by_mood`

**Purpose**: Retrieves tracks previously tagged with a mood.

**Arguments**:

- `mood` (string).
- `limit` (int, default=20).

## ⚖️ Quality Control & Execution

### `assess_playlist_quality`

**Purpose**: (The "Bliss" Logic) Analyzes a list of candidate Song IDs for diversity.

**Arguments**:

- `song_ids` (List[string]).

**Returns**: JSON containing:

- `diversity_score` (0.0 to 1.0)
- `most_repetitive_artist` (Object with count and warning boolean)
- `genres_detected` (List)

### `create_playlist`

**Purpose**: Finalizes the action by saving the playlist to Navidrome.

**Arguments**:

- `name` (string).
- `song_ids` (List[string]).