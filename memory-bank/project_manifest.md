# Project: NaviGravity (NG)

## Vision

We are building an Agentic Music Curator that connects a Large Language Model (Antigravity/Gemini) to a self-hosted Navidrome music server via the Model Context Protocol (MCP).

The goal is to move beyond simple "search and play" to complex, reasoned curation that understands user taste, technical quality, and library statistics.

## Core Philosophy

1. **Non-Invasive Moods (Virtual Tags)**: We DO NOT modify audio files. Moods are stored as System Playlists (e.g., `System:Mood:Energetic`).

2. **The "Bliss" Quality Gate**: The AI must criticize its own selection. Before saving a playlist, it must run a quality assessment (artist repetition, genre consistency).

3. **Smart Discovery**: We use statistical algorithms (Magic Lists) to find "Forgotten Gems" or "Hidden Tracks" rather than relying solely on text search.

4. **Divergence**: The system must be able to break the "Filter Bubble" by suggesting genres the user rarely listens to.

## Licensing & Contribution

- **License**: [MIT (Open Source)](../LICENSE).
- **Social Contract**: Users are encouraged to attribute the work and contribute back improvements via PRs (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

## Architecture

For a detailed breakdown of the MCP architecture, see [MCP Architecture & Workflow](mcp_architecture.md).
For guidelines on how the Agent should use these tools, see [LLM Tool Usage Manifesto](llm_tool_usage.md).

- **Brain**: Antigravity (Google Gemini) via MCP Client.
- **Protocol**: MCP (Model Context Protocol).
- **Server**: A local Python script (navidrome_mcp_server.py) acting as the MCP Host.
- **Storage**: Navidrome (Subsonic API).
- **Quality Assurance**: Automated testing via `pytest` with `libsonic` mocking.
- **Feedback Loop**: Analytical Logging (JSON) to track LLM inputs vs. result quality for continuous improvement.

## Workflow

1. **User Prompt**: "I want a high-energy playlist for coding."

2. **Tool Selection**: Agent calls get_tracks_by_mood('focus') or search_music_enriched('electronic').

3. **Refinement**: Agent calls assess_playlist_quality on the candidate list.

4. **Correction**: If quality is low (e.g., too much repetition), Agent swaps tracks.

5. **Execution**: Agent calls create_playlist.

## Development & Testing

We employ a "Test First" (or at least "Test Always") methodology using mocks to ensure server stability without requiring a live Navidrome instance for every check.

- **Framework**: `pytest`
- **Mocking**: `pytest-mock` for simulating Subsonic API responses.
- **Coverage**: Core logic for discovery, recommendations, and mood tagging is unit tested.

## Maintenance & Operations

### Analytical Feedback Loop
We maintain a continuous improvement cycle for the Agent's performance:
1. **Log Review**: Periodically analyze `logs/navidrome_mcp.log` to identify:
   - "Empty Result" queries (indicates bad prompts or overly strict logic).
   - "Low Diversity" playlists (indicates need for better shuffling or source pools).
2. **Refinement**: Use these insights to update the LLM system prompts or server logic (e.g., adding fallback searches).