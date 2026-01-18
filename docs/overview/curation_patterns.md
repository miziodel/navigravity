# Navidrome Advanced Playlist Curation Patterns

## 1. Core Curation Strategies

### A. The "Focus Flow" (BPM & Era)
Creating effective work/focus playlists requires more than just genre filtering.
- **Mood Base**: Start with `manage_playlist(name='NG:Mood:Focus', operation='get')` to ground the list in known favorites.
- **BPM Zoning**: Tracks between **70-130 BPM** are ideal for maintaining momentum without inducing anxiety.
- **Organic Transitions**: Sorting a playlist by BPM (Low → High) can create a natural "ramp up" effect, useful for starting a work session.
- **Recency Filter**: To avoid "Oldies" bias in Jazz/Electronic, filter by `Year > (Current - 5)`. This surfaces modern, relevant production styles.

### B. Verification of "Unheard" Content
- **Hidden Gems (Library Wide)**: `playCount == 0` across the entire library is good for deep mining.
- **Unheard Favorites (Starred Albums)**: A more refined strategy is `playCount == 0` *within* Starred Albums. This ensures the user *likes* the artist but hasn't explored the specific track.
- **The "Round Robin" Diversity Fix**: When mining albums, don't take all unplayed tracks from Album A then Album B. Instead, take 1 from A, 1 from B, 1 from C, then loop back. This prevents "clumps" of the same artist in the final list.

## 2. Agentic Discovery Workflow

### The "Map & Mine" Pattern
Blindly searching for "Electronic" often yields generic results. A better approach:
1.  **Map**: Use `get_genres()` to list all tags.
2.  **Filter**: Agentically select sub-genres that match the semantic goal (e.g., for "Focus": "IDM", "Glitch", "Folktronica", "Chamber Jazz").
3.  **Verify**: Use `explore_genre(tag)` to ensure the tag contains artists relevant to the goal.
4.  **Mine**: Fetch tracks specifically from these validated sub-genres (e.g. `get_genre_tracks`).

## 3. Strict Quality Gates
For listener satisfaction, agentic playlists should enforce:
- **Max Tracks per Artist**: Hard limit of 3.
- **Min Unique Artists**: For a 50-track playlist, aim for >30 unique artists.
- **Vocal Exclusion**: For "Focus" or "Mellow" playlists, strict exclusion of "Vocal Jazz" or "Pop" genres is safer than relying on metadata which often lacks "Instrumental" tags.

**Exceptions**:
These constraints can be relaxed *only* if the user explicitly requests a narrow scope (e.g. "Best of Miles Davis", "1999 Hip Hop") AND there is insufficient content to fill the playlist otherwise. In such cases, prioritize fulfilling the user's specific constraint over general diversity rules.

## 4. Draft Blueprints
Detailed curation strategies currently under development.

- **[The Universal Bridge (A ➔ B)](../architecture/blueprints/universal_bridge_draft.md)**: A 30-40 track sequence connecting distant musical worlds via resonance nodes.

## 5. Technical Implementation Notes
- **Libsonic URL Parsing**: `libsonic` connection requires strictly parsed URLs (scheme/host separate from port).
- **Subsonic API**: `getAlbumList2` uses `ltype` (list type) argument, not `type`.
- **Genre Mining**: `getRandomSongs(genre=...)` is the most efficient way to get candidates for a mood without downloading the entire database.
