# NaviGravity Roadmap

## 🗺️ Roadmap (Backlog)

- **Remote Access (SSE)**: Implement Server-Sent Events (SSE) transport to allow remote clients to connect to NaviGravity (currently local stdio only).
- **Gap Analysis**: Automate the "Dual Identity" check to periodically suggest missing artists.

## 🔄 Recurring / Operations
- **Analytical Review**: Bi-weekly analysis of `logs/navidrome_mcp.log` to identify:
  - "Empty Result" queries (bad prompts?).
  - "Low Quality" playlists (bad logic?).
  - Refine system prompts based on findings.

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
