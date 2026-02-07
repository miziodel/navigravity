# Discovery Recipe: The Unheard Giants (Cross-Genre Pillars)

This recipe is designed to revitalize a music library by surface-mining "hidden giants"—legendary tracks by pillar artists that have never been played.

## 📝 Objective
Create a high-quality, diverse 50-track playlist of unplayed tracks (Play Count = 0) from the library's most significant "Pillar Artists" across multiple genre clusters.

## 🛠 Tools & Ingredients

### Ingredients (Logic Filters):
*   **Play Count:** Exactly 0 (or Never Played).
*   **Artist Significance:** Must be a "Pillar" (High album count or historically legendary).
*   **Diversity Constraint:** No more than 2% of tracks per single artist (ensures a wide breadth of discoveries).
*   **Genre Coverage:** Comprehensive representation of all primary genres found in the library, including but not limited to: Classical, Jazz, Soul, Funk, R&B, Rock, Prog, Italian Songbook, Hard Rock, Metal, Electronic, etc.

### Tools (Navigravity API):
*   `analyze_library(mode='pillars')`: To identify the foundation of the library.
*   `get_smart_candidates(mode='hidden_gems')`: To fetch high-score tracks with 0 plays.
*   `search_music_enriched(query='Artist Name')`: To deep-dive into specific legendary catalogs for unplayed versions/takes.
*   `assess_playlist_quality()`: To verify the diversity score and artist repetition.

## 👨‍🍳 Preparation Steps

### 1. Identify the Foundations
Analyze the library to find the top 20-30 artists by album count. Cross-reference these with "Legendary" status (e.g., Bach, Miles Davis, Pink Floyd).

### 2. Mining the Gaps
For each identified artist, query for tracks with `play_count: 0`.

> [!TIP]
> Focus on specialized editions (Remasters, Live recordings, Anniversary editions) as these often contain legendary performances that go unheard.

### 3. Clustering
Group the found tracks by their primary genre. Map these to the library's top-level genres to ensure no single style dominates the selection.

### 4. Balancing & Final Mix
Select ~7 tracks per cluster. Ensure the transition flow makes sense (Chronological or Energy-based).

### 5. Deployment
Batch create the playlist on the Navidrome server using `manage_playlist(operation='create')`.

## 🌶️ Optional Flavor Modules
These optional enhancements can be combined with the base recipe to create more specialized playlists.

### 🕰️ Era Diversity
Balance the selection across decades (60s, 70s, 80s, 90s, 2000s+) for a richer temporal journey through music history.
*   **Implementation:** Group candidates by year, ensure no decade exceeds 25% of the playlist.

### 🎬 Deep Cuts Only
Exclude obvious "greatest hits" and focus on lesser-known album tracks.
*   **Implementation:** Filter out tracks that appear on compilation albums or have historically high play counts across the library.

### 📈 BPM Flow
Order the final playlist by ascending or descending energy for a more narrative listening experience.
*   **Implementation:** Sort by `bpm` field. Consider "Warm-up → Peak → Cool-down" structure.

### ⭐ Starred but Unheard
Include tracks that were "starred" but never actually played—forgotten intentions waiting to be rediscovered.
*   **Implementation:** Use `get_smart_candidates(mode='unheard_favorites')`.

### 🔀 Divergent Gems
Find stylistically unusual tracks for each artist—the unexpected side of legends.
*   **Implementation:** Use `get_smart_candidates(mode='divergent')` to surface genre-bending rarities.

### 📉 Fallen Pillars
Resurface artists you used to listen to heavily but have neglected lately.
*   **Implementation:** Use `get_smart_candidates(mode='fallen_pillars')` to identify dormant favorites.

### 🎛️ Strict Artist Limit
For maximum variety, enforce a hard cap of 1-2 tracks per artist.
*   **Implementation:** Set `max_tracks_per_artist: 1` in the filtering rules.

## 📈 Yield & Quality
*   **Expected Results:** 50 tracks.
*   **Diversity Target:** > 0.75 diversity score.
*   **User Impact:** High nostalgia and discovery value with zero "skip" risk from overplayed hits.
