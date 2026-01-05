# NaviGravity (Navidrome Agentic Curator) 🎧

**NaviGravity** (NG) is an intelligent MCP (Model Context Protocol) server that empowers an AI agent to act as a sophisticated music curator for your self-hosted [Navidrome](https://www.navidrome.org/) library.

Unlike simple search tools, NG implements a specific curation philosophy focused on quality, discovery, and non-destructive library management.

## 🧠 Core Philosophy

1.  **The "Bliss" Quality Gate**: The AI acts as a critic. No playlist is created without passing a `assess_playlist_quality` check to ensure diversity and prevent artist repetition.
2.  **Virtual Tags (Non-Invasive)**: We treat your audio files as sacred read-only artifacts. Moods and custom tags are stored as "System Playlists" (e.g., `System:Mood:Focus`), keeping your file metadata clean.
3.  **Smart Discovery**: Features "Magic List" algorithms to surface Forgotten Gems, Hidden Tracks, and divergent genres to break your filter bubble.

## Setup & Installation

Follow these steps to set up the development environment.

**Prerequisites:**
-   **Python 3.10+**
-   A running **Navidrome** server and user account

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd navigravity
    ```

2.  **Create and activate a Python virtual environment (Required):**
    > **Note:** Antigravity and developers must always use a virtual environment to manage dependencies.

    ```bash
    # Ensure python3 is version 3.10+
    # If your system python is older, use: python3.11 -m venv .venv
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    Copy `.env.example` to `.env` (create one if needed) and set your Navidrome credentials:
    ```env
    NAVIDROME_URL=http://your-navidrome-instance:4533
    NAVIDROME_USER=your_username
    NAVIDROME_PASS=your_password
    ```

## 🚀 Usage

## 🚀 Usage

**Important**: This is an [MCP](https://modelcontextprotocol.io/) server. It runs strictly as a backend process for an AI Client (like Claude Desktop, Zed, or Antigravity). You do NOT need to "visit" it in a browser.

For a deep dive into how strict coordination works without a UI, see [MCP Architecture & Workflow](memory-bank/mcp_architecture.md).

### Running via MCP Client (Recommended)
Add the following to your client's configuration (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "navidrome": {
      "command": "/path/to/navigravity/.venv/bin/python",
      "args": ["/path/to/navigravity/src/navidrome_mcp_server.py"]
    }
  }
}
```

Once configured, the client will automatically start/stop the server as needed.

## 🤖 For Agents & Curators

We provide a specialized guide for the Large Language Models interacting with this toolset. It defines the "Curator Persona", "Bliss Quality Gate" protocols, and strategic patterns (e.g., *The Time Machine* or *Semantic Exploration*).

👉 **[Read the LLM Tool Usage Manifesto](memory-bank/llm_tool_usage.md)**

## 🧰 Available Tools

The agent has access to the following tools:

-   **Discovery**:
    -   `get_genres`: Lists all library genres with track counts.
    -   `explore_genre`: Deep dive into a specific genre (artists, albums).
    -   `get_genre_tracks`: Fetches random tracks from a genre.
    -   `get_smart_candidates`: Statistical discovery (Rediscover, Hidden Gems, Unheard Favorites).
    -   `get_divergent_recommendations`: Suggests genres you rarely listen to.
    -   `search_music_enriched`: Metadata-rich search.
    -   `artist_radio`: Smart mixing of artist/similar tracks.
    -   `get_sonic_flow`: BPM/Linkage matching.

-   **Curation**:
    -   `set_track_mood` / `get_tracks_by_mood`: Manage Virtual Tags.
    -   `assess_playlist_quality`: The "Bliss" check logic.
    -   `create_playlist`: Final execution step.

---

## Development

### Auto-reload
For development with auto-reload, use the `mcp dev` command:
```bash
mcp dev src/navidrome_mcp_server.py
```
This will launch the MCP Inspector, which provides a web interface to test your tools and automatically reloads the server when you modify the code.

## 📜 License & Contributing

This project is open-source under the **MIT License**.

- **Freedom**: You are free to use, modify, and distribute this code.
- **Our Request**: Please attribute the authors and consider contributing your changes back to the community via Pull Requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on our open philosophy.

> [!NOTE]
> This project depends on libraries like `py-sonic` which are licensed under **GPLv3**. While our code is MIT, bundling it with GPL dependencies may affect the licensing of distributed binaries.

---
*Built with ❤️ for the self-hosted music community.*
