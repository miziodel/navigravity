# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

__version__ = "0.1.6"

from mcp.server.fastmcp import FastMCP
import libsonic
import os
import sys
import json
import random
import datetime
from collections import Counter
from typing import Optional, List, Dict
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
import logging
from pythonjsonlogger import jsonlogger
import time
import functools

# --- CONFIGURATION ---
# Load .env from the project root (one level up from src/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

NAVIDROME_URL = os.getenv("NAVIDROME_URL")
NAVIDROME_USER = os.getenv("NAVIDROME_USER")
NAVIDROME_PASS = os.getenv("NAVIDROME_PASS")

if not all([NAVIDROME_URL, NAVIDROME_USER, NAVIDROME_PASS]):
    raise ValueError("Missing Navidrome configuration. Please ensure NAVIDROME_URL, NAVIDROME_USER, and NAVIDROME_PASS are set in your .env file.")


# --- LOGGING SETUP ---
logger = logging.getLogger("navidrome_mcp")
logger.setLevel(logging.INFO)

# File Handler (JSON) - Writable by user running the script
# --- LOGGING SETUP ---
logger = logging.getLogger("navidrome_mcp")
logger.setLevel(logging.INFO)

# Formatter
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"levelname": "level", "asctime": "timestamp"},
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)

# 1. Standard Error Handler (Default / Cloud Native)
# This ensures logs are always visible to the MCP Client (like Claude Desktop)
# without requiring write permissions to the file system.
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)

# 2. Optional File Handler (User Configured)
# If NAVIDROME_LOG_FILE is set in .env, we also log to that file.
# Useful for persistent debugging.
log_file_path = os.getenv("NAVIDROME_LOG_FILE")

if log_file_path:
    try:
        # Resolve path relative to project root if it's not absolute
        # We assume the user creates the directory or it exists.
        log_path = Path(log_file_path)
        if not log_path.is_absolute():
            # Fallback assumption: relative to where the script is run (usually project root)
            # or relative to project_root if defined
            project_root = Path(__file__).parent.parent
            log_path = project_root / log_path

        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file enabled: {log_path}", extra={"action": "startup_log_config"})
    except Exception as e:
        # Don't crash if file logging fails, just warn to stderr
        logger.error(f"Failed to setup file logging: {e}", extra={"action": "startup_log_error"})

# Metadata capture decorator
def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = func.__name__
        
        # Capture input args (convert to clean dict if needed)
        input_data = {"args": args, "kwargs": kwargs}
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            # Analyze result for logging without dumping huge payloads
            result_meta = {}
            if isinstance(result, str):
                try:
                    # Try to parse JSON results to get counts
                    parsed = json.loads(result)
                    if isinstance(parsed, list):
                        result_meta["count"] = len(parsed)
                        result_meta["ids"] = [item.get("id") for item in parsed if isinstance(item, dict) and "id" in item]
                    elif isinstance(parsed, dict):
                        # Catch quality assessment scores
                        if "diversity_score" in parsed:
                            result_meta["diversity_score"] = parsed["diversity_score"]
                            result_meta["repetition_warning"] = parsed.get("most_repetitive_artist", {}).get("warning")
                except:
                    result_meta["raw_length"] = len(result)
            
            logger.info(
                "Tool execution successful",
                extra={
                    "tool": tool_name,
                    "inputs": input_data,
                    "result_summary": result_meta,
                    "duration_ms": round(duration, 2)
                }
            )
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                "Tool execution failed",
                extra={
                    "tool": tool_name,
                    "inputs": input_data,
                    "error": str(e),
                    "duration_ms": round(duration, 2)
                },
                exc_info=True
            )
            raise e
            
    return wrapper

mcp = FastMCP("Navidrome Agentic Server")

def get_conn():
    # Parse the URL to separate scheme/host from port
    parsed = urlparse(NAVIDROME_URL)
    
    # Construct base URL (scheme + hostname)
    # Note: libsonic constructs the full URL by appending :{port} provided in constructor
    base_url = f"{parsed.scheme}://{parsed.hostname}"
    
    # Extract port, default to 80 or 443 if not present
    port = parsed.port
    if not port:
        port = 443 if parsed.scheme == 'https' else 80
        
    return libsonic.Connection(
        baseUrl=base_url, 
        username=NAVIDROME_USER, 
        password=NAVIDROME_PASS, 
        port=port,
        appName="AntigravityMCP"
    )

def _format_song(s):
    return {
        "id": s.get('id'),
        "title": s.get('title'),
        "artist": s.get('artist'),
        "album": s.get('album'),
        "year": s.get('year'),
        "genre": s.get('genre', 'Unknown'),
        "duration": s.get('duration', 0),
        "bpm": s.get('bpm', 0),
        "play_count": s.get('playCount', 0),
        "last_played": s.get('played', 'Never'),
        "starred": "starred" in s,
        "rating": s.get('userRating', 0),
        # Attempt to extract mood/subgenre if available in comments or other fields
        # Navidrome doesn't always expose these directly in getSong, but we can try
        "comment": s.get('comment', ''), 
        "path": s.get('path', '')
    }

def _fetch_albums(criteria: str, size: int = 50, genre: str = None) -> List[Dict]:
    """
    Wrapper for getAlbumList2 to abstract 'ltype' parameter.
    Criteria: 'frequent', 'newest', 'starred', 'random', 'alphabeticalByName', 'byGenre'
    """
    conn = get_conn()
    try:
        if criteria == 'byGenre' and genre:
            res = conn.getAlbumList2(ltype=criteria, genre=genre, size=size)
        else:
            res = conn.getAlbumList2(ltype=criteria, size=size)
        return res.get('albumList2', {}).get('album', [])
    except Exception as e:
        logger.error(f"Failed to fetch albums for criteria {criteria}: {e}")
        return []


# --- RESOURCES & PROMPTS: DISCOVERY & INFO ---

@mcp.resource("navidrome://info")
def get_server_info() -> str:
    """Returns server identity, version, and connectivity status."""
    return json.dumps({
        "server": "Navigravity",
        "version": __version__,
        "status": "connected", # Static for now, could be dynamic
        "capabilities": ["playback", "playlists", "discovery", "curation"]
    })

@mcp.tool()
def check_connection() -> str:
    """Verifies connection to the backend Navidrome instance."""
    try:
        conn = get_conn()
        if conn.ping():
            # Clean up the URL in case it has user info
            safe_url = conn.baseUrl.split('@')[-1] if '@' in conn.baseUrl else conn.baseUrl
            return f"Connected to Navidrome at {safe_url}"
        return "Failed to connect to Navidrome (ping failed)"
    except Exception as e:
        return f"Failed to connect to Navidrome: {str(e)}"

@mcp.prompt()
def usage_guide() -> str:
    """Returns the 'Instruction Manual' for the Navigravity MCP server."""
    return """
    # Navigravity MCP Server Guide
    
    ## 1. Discovery
    - Start by checking `navidrome://info` to see server capabilities.
    - Use `check_connection` to verify the backend is up.
    
    ## 2. Exploration
    - `get_genres()`: See what's available.
    - `explore_genre(genre)`: deep dive into a genre.
    - `analyze_library(mode='taste_profile')`: Understand the user's taste.
    
    ## 3. Curation (The Quality First Workflow)
    Follow the Curator Manifesto:
    1. **Harvest**: Use `get_smart_candidates` to get raw tracks.
    2. **Filter**: Use `assess_playlist_quality` (if available) or `batch_check_library_presence`.
    3. **Execute**: Use `manage_playlist` to create the final playlist.
    
    ## 4. Playback
    - This server primarily manages library state. Playback control depends on your specific client integration.
    """

# --- RESOURCES & PROMPTS: CURATOR ---

CURATOR_MANIFESTO_TEXT = """
# The Curator Manifesto
> "L'agente 'bibliotecario' è morto. Viva il Curatore."

This protocol defines the strict **Quality First** methodology for all playlist generation tasks. No more "trial and error". 

## 1. The Core Philosophy
**Stop Guessing. Start Curating.**
Every playlist must pass through three rigorous stages: **Harvest ➔ Filter ➔ Execute**.

## 2. The Information Hierarchy
Reliability over Randomness.
1.  **Harvest (The Broad Net)**: Gather 3x-5x the required tracks.
    *   *Target*: 150+ candidates for a 50-song playlist.
    *   *Tools*: `get_smart_candidates`, `search_music_enriched`.
2.  **Filter (The Quality Gate)**: Ruthlessly cull candidates.
    *   *Diversity Check*: Use `assess_playlist_quality` to ensure no artist dominates (max 2-3 tracks per artist unless specified).
    *   *Library Presence*: Use `batch_check_library_presence` to verify availability.
    *   *Analysis*: Check `diversity_score` and `repetition_metrics`.
3.  **Execute (The Precision Strike)**: Create the final product.
    *   *Action*: `manage_playlist` (create).
    *   *Verification*: Final `assess_playlist_quality` run on the created playlist.

## 3. The Rules of Engagement
*   **Harvest Ratio**: Always fetch **300%-500%** of the target length.
*   **Quality Gate**: NEVER create a playlist without passing the `assess_playlist_quality` check first.
*   **Batch Verification**: NEVER assume tracks exist; verify them.

## 4. Operational Workflow
1.  **Request Analysis**: Understand the vibe/genre/mood.
2.  **Harvesting**:
    *   Call `get_smart_candidates(limit=150, ...)`
3.  **Filtering**:
    *   Local processing to filter duplicates and heavy repetition.
    *   Consult `assess_playlist_quality` on the draft list.
4.  **Finalization**: 
    *   Push to server via `manage_playlist`.

---
*Signed: The Curator*
"""

@mcp.resource("curator://manifesto")
def get_manifesto() -> str:
    """Returns the Curator Manifesto protocol."""
    return CURATOR_MANIFESTO_TEXT

@mcp.prompt()
def curator_mode() -> str:
    """Injects the Curator Manifesto into the context to enforce strict playlist quality protocols."""
    return f"""
    You are now operating in CURATOR MODE. 
    Review the following protocol strictly before proceeding with any playlist task.
    
    {CURATOR_MANIFESTO_TEXT}
    """


# --- TOOLS: ANALYSIS & INTROSPECTION ---

@mcp.tool()
@log_execution
def analyze_library(mode: str = "composition") -> str:
    """
    Analyzes the library inventory and user stats.
    
    Args:
        mode: The type of analysis to perform.
            - 'composition': Returns genre distribution and total stats (Cold Analysis).
            - 'pillars': Identifies core artists (Album Count) (Canonical Analysis).
            - 'taste_profile': Analyzes recent/frequent/starred for top artists & eras (Warm Analysis).
    """
    conn = get_conn()
    try:
        if mode == "composition":
            # Get all genres
            res = conn.getGenres()
            genres = res.get('genres', {}).get('genre', [])
            
            # Sort by song count
            genres.sort(key=lambda x: x.get('songCount', 0), reverse=True)
            
            # Calculate totals
            total_songs = sum(g.get('songCount', 0) for g in genres)
            total_albums = sum(g.get('albumCount', 0) for g in genres)
            
            # Format top 30 genres
            top_genres = []
            for g in genres[:30]:
                top_genres.append({
                    "name": g.get('value'),
                    "song_count": g.get('songCount'),
                    "album_count": g.get('albumCount'),
                    "percentage": round((g.get('songCount', 0) / total_songs * 100), 2) if total_songs > 0 else 0
                })
                
            return json.dumps({
                "total_stats": {
                    "songs": total_songs,
                    "albums": total_albums,
                    "genres": len(genres)
                },
                "composition": top_genres
            }, indent=2)

        elif mode == "pillars":
            # NOTE: libsonic's getArtists() usually maps to getIndexes.
            response = conn.getArtists()
            all_artists = []
            
            # Subsonic API can return 'artists' or 'indexes' root
            artists_root = response.get('artists') or response.get('indexes')
            if artists_root and 'index' in artists_root:
                for index_entry in artists_root['index']:
                    if 'artist' in index_entry:
                        all_artists.extend(index_entry['artist'])
                        
            all_artists.sort(key=lambda x: int(x.get('albumCount', 0)), reverse=True)
            
            pillars = []
            for a in all_artists[:50]:
                pillars.append({
                    "name": a.get('name'),
                    "album_count": int(a.get('albumCount', 0)),
                    "id": a.get('id')
                })
            return json.dumps(pillars, indent=2)

        elif mode == "taste_profile":
            freq = _fetch_albums("frequent", size=100)
            recent = _fetch_albums("newest", size=100)
            starred = _fetch_albums("starred", size=100)
            
            combined = freq + recent + starred
            
            artists = []
            genres = []
            years = []
            
            for alb in combined:
                if alb.get('artist'): artists.append(alb['artist'])
                if alb.get('genre'): genres.append(alb['genre'])
                if alb.get('year'): years.append(alb['year'])
                
            top_artists = [a[0] for a in Counter(artists).most_common(50)]
            top_genres = [g[0] for g in Counter(genres).most_common(20)]
            
            eras = []
            if years:
                decades = [int(y)//10*10 for y in years if str(y).isdigit()]
                top_decades = [f"{d}s" for d, _ in Counter(decades).most_common(3)]
                eras = top_decades
                
            return json.dumps({
                "top_artists": top_artists,
                "top_genres": top_genres,
                "favorite_eras": eras,
                "total_albums_analyzed": len(combined)
            }, indent=2)
        
        else:
            return f"Unknown mode: {mode}"

    except Exception as e: return str(e)

@mcp.tool()
@log_execution
def batch_check_library_presence(query: List[Dict[str, str]]) -> str:
    """
    Checks if artists/albums exist in the library.
    Input example: [{"artist": "Camel"}, {"artist": "Pink Floyd", "album": "Animals"}]
    """
    conn = get_conn()
    results = []
    
    # Optimization: Cache all artist names if query is large? 
    # For now, safe iterative search is robust enough for typical batch sizes (10-20).
    
    for item in query:
        artist = item.get("artist")
        album = item.get("album")
        
        if not artist: continue
        
        status = {"artist": artist, "present": False, "type": "artist"}
        
        try:
            if album:
                status["type"] = "album"
                status["album"] = album
                # Specific album search
                # Quote the query to ensure better exact matching behavior if supported,
                # but search3 is "smart". Composite string "Artist Album" usually works well.
                query_str = f'"{artist}" "{album}"'
                search_response = conn.search3(query_str, albumCount=1)
                
                # Verify exact matches in returned albums
                found = False
                search_data = search_response.get('searchResult3', {})
                if 'album' in search_data:
                    for alb_record in search_data['album']:
                        # Loose string match to tolerate "The Wall" vs "Wall"
                        if artist.lower() in alb_record.get('artist', '').lower() and \
                           album.lower() in alb_record.get('title', '').lower():
                            found = True
                            break
                status["present"] = found
                
            else:
                # Artist only search
                search_response = conn.search3(f'"{artist}"', artistCount=1)
                found = False
                search_data = search_response.get('searchResult3', {})
                if 'artist' in search_data:
                    for art_record in search_data['artist']:
                        if artist.lower() == art_record.get('name', '').lower():
                            found = True
                            break
                status["present"] = found
                
        except Exception as e:
            status["error"] = str(e)
            
        results.append(status)
        
    return json.dumps(results, indent=2)

# --- TOOLS: DISCOVERY ---

@mcp.tool()
@log_execution
def get_genre_tracks(genre: str, limit: int = 100) -> str:
    """Fetches random tracks for a specific genre."""
    conn = get_conn()
    try:
        # Try getRandomSongs with genre filter first (most efficient for discovery)
        # Note: libsonic might not support genre arg in getRandomSongs directly in all versions,
        # but Subsonic API 1.16.1+ supports it.
        # If kwargs are passed through, this works.
        res = conn.getRandomSongs(size=limit, genre=genre)
        songs = res.get('randomSongs', {}).get('song', [])
        
        # Fallback: if empty, maybe try getSongsByGenre if it exists (usually for specific browsing)
        if not songs:
            try:
                # Some clients/servers use this
                res = conn.getSongsByGenre(genre, count=limit)
                songs = res.get('songsByGenre', {}).get('song', [])
            except:
                pass
                
        output = [_format_song(s) for s in songs]
        return json.dumps(output, indent=2)
    except Exception as e: return str(e)


@mcp.tool()
@log_execution
def get_genres() -> str:
    """Lists all available genres with track and album counts."""
    conn = get_conn()
    try:
        res = conn.getGenres()
        genres = res.get('genres', {}).get('genre', [])
        # Sort by song count descending for utility
        genres.sort(key=lambda x: x.get('songCount', 0), reverse=True)
        
        output = []
        for g in genres:
            output.append({
                "name": g.get('value') or g.get('name'), # value is standard, name sometimes used
                "tracks": g.get('songCount'),
                "albums": g.get('albumCount')
            })
        return json.dumps(output, indent=2)
    except Exception as e: return str(e)

@mcp.tool()
@log_execution
def explore_genre(genre: str, limit: int = 50) -> str:
    """Gets detailed metrics for a genre (Top Artists, Album counts)."""
    conn = get_conn()
    try:
        # Fetch albums by genre
        # Note: size limit applies to albums. 500 is a good sample size.
        albums = _fetch_albums("byGenre", size=500, genre=genre)

        
        artist_stats = {}
        
        for alb in albums:
            art = alb.get('artist')
            if art not in artist_stats:
                artist_stats[art] = {"count": 0, "albums": []}
            artist_stats[art]["count"] += 1
            artist_stats[art]["albums"].append(alb.get('title'))
            
        # Convert to list and sort by album count
        sorted_artists = sorted(
            [{"name": k, "album_count": v["count"], "albums": v["albums"]} for k,v in artist_stats.items()],
            key=lambda x: x['album_count'],
            reverse=True
        )
        
        output = {
            "genre": genre,
            "total_albums_found": len(albums),
            "unique_artists": len(sorted_artists),
            "top_artists": sorted_artists[:limit]
        }
        return json.dumps(output, indent=2)
    except Exception as e: return str(e)


@mcp.tool()
@log_execution
def get_smart_candidates(
    mode: str, 
    limit: int = 50,
    include_genres: List[str] = None,
    exclude_genres: List[str] = None,
    min_bpm: int = None,
    max_bpm: int = None,
    mood: str = None,
    max_tracks_per_artist: int = None
) -> str:
    """
    Generates lists based on stats with advanced filtering.
    
    Args:
        mode: recently_added, most_played, top_rated, lowest_rated, rediscover, hidden_gems, unheard_favorites, divergent
        limit: Max tracks to return (default 50)
        include_genres: List of genres to strictly include (case-insensitive partial match)
        exclude_genres: List of genres to exclude
        min_bpm: Minimum BPM
        max_bpm: Maximum BPM
        mood: 'relax' (low BPM, no heavy genres), 'energy' (high BPM, upbeat genres), etc.
        max_tracks_per_artist: Diversity constraint
    """
    conn = get_conn()
    try:
        # --- 1. MOOD MAPPING (INFERENCE) ---
        # Map high-level mood to low-level technical constraints
        if mood:
            mood = mood.lower()
            if mood == "relax":
                # Implicit filters: Slow to mid tempo, avoid aggressive genres
                if max_bpm is None: max_bpm = 115
                if exclude_genres is None: exclude_genres = []
                exclude_genres.extend(["Metal", "Hard Rock", "Punk", "Industrial", "Techno", "Drum and Bass"])
            elif mood == "energy" or mood == "workout":
                if min_bpm is None: min_bpm = 120
                if include_genres is None: include_genres = []
                # We don't strictly enforce include_genres for energy as many genres can be energetic,
                # but we rely on BPM. Optionally we could favor Pop/Rock/Electronic.
            elif mood == "focus":
                if exclude_genres is None: exclude_genres = []
                exclude_genres.extend(["Pop", "Hip-Hop", "Rap", "Vocal"]) # Try to avoid distracting lyrics
                
        # --- 2. FETCH CANDIDATES (Raw Pool) ---
        # We fetch a larger pool to allow for filtering attrition
        fetch_limit = limit * 5 if (include_genres or exclude_genres or min_bpm or max_bpm) else limit * 2
        # Cap fetch limit to avoid timeout
        if fetch_limit > 500: fetch_limit = 500
        
        candidates = []
        # ... fetch logic per mode ...
        
        if mode == "recently_added":
            albums = _fetch_albums("newest", size=fetch_limit)
            # Just return representative tracks (track 1) from new albums for discovery
            for alb in albums:
                 try:
                     # Peek at first song
                     res = conn.getMusicDirectory(alb['id'])
                     songs = res.get('directory', {}).get('child', [])
                     if songs:
                         # Filter only songs
                         songs = [s for s in songs if not s.get('isDir')]
                         if songs: candidates.append(_format_song(songs[0]))
                 except: continue

        elif mode == "most_played":
            # Heuristic: Get frequent albums, then extract their top songs
            # INCREASED SIZE: Fetch more albums to ensure we get a true Top 30+ even if some albums are short
            frequent_albums = _fetch_albums("frequent", size=fetch_limit)  
            all_tracks = []
            for alb in frequent_albums:
                try:
                    res = conn.getMusicDirectory(alb['id'])
                    songs = res.get('directory', {}).get('child', [])
                    all_tracks.extend([s for s in songs if not s.get('isDir')])
                except: continue
            
            # Sort all gathered tracks by playCount
            all_tracks.sort(key=lambda x: x.get('playCount', 0), reverse=True)
            # Remove duplicates based on ID (though rare here)
            seen = set()
            for t in all_tracks:
                if t['id'] not in seen:
                    candidates.append(_format_song(t))
                    seen.add(t['id'])

        elif mode == "top_rated":
            # 1. Get Starred Songs
            starred_res = conn.getStarred()
            if 'starred' in starred_res and 'song' in starred_res['starred']:
                candidates.extend([_format_song(s) for s in starred_res['starred']['song']])
            
            # 2. Get High Rated (Hearts) - Heuristic via random sampling if no direct endpoint
            # We assume userRating >= 3 is "Good"
            # Note: A full scan is expensive, so we sample heavily
            pool = conn.getRandomSongs(size=500)
            if 'randomSongs' in pool and 'song' in pool['randomSongs']:
                for s in pool['randomSongs']['song']:
                    if s.get('userRating', 0) >= 3:
                        candidates.append(_format_song(s))
            
            # Deduplicate by ID
            unique_candidates = {c['id']: c for c in candidates}
            candidates = list(unique_candidates.values())
            
            # Sort: Priority to Play Count (Active Favorites)
            candidates.sort(key=lambda x: x.get('playCount', 0), reverse=True)

        elif mode == "lowest_rated":
            # Hunt for tracks with userRating 1 or 2
            # DEEP SCAN: Retries to find enough candidates
            found_count = 0
            retries = 3
            sample_size = fetch_limit * 2 # Aggressive sampling
            
            for _ in range(retries):
                if found_count >= limit: break
                
                pool = conn.getRandomSongs(size=sample_size)
                if 'randomSongs' in pool and 'song' in pool['randomSongs']:
                    for s in pool['randomSongs']['song']:
                        rating = s.get('userRating', 0)
                        if 1 <= rating <= 2:
                            fmt = _format_song(s)
                            # Avoid duplicates across retries
                            if not any(c['id'] == fmt['id'] for c in candidates):
                                candidates.append(fmt)
                                found_count += 1
            
            # Sort by play count (maybe you hate-listened to them?)
            candidates.sort(key=lambda x: x.get('playCount', 0), reverse=True)

        elif mode in ["rediscover", "forgotten_favorites", "hidden_gems"]:
            pool = conn.getRandomSongs(size=fetch_limit * 2) # Fetch extra for date filtering
            today = datetime.datetime.now()
            if 'randomSongs' in pool and 'song' in pool['randomSongs']:
                for s in pool['randomSongs']['song']:
                    lp_str = s.get('played')
                    pc = s.get('playCount', 0)
                    starred = "starred" in s
                    
                    if mode == "hidden_gems" and pc == 0:
                        candidates.append(_format_song(s))
                        continue
                        
                    if lp_str:
                        # Handle potential Z timezone or no Z
                        try:
                            lp_date = datetime.datetime.fromisoformat(lp_str.replace("Z", ""))
                            days = (today - lp_date).days
                            if mode == "rediscover" and days > 365 and pc > 2:
                                candidates.append(_format_song(s))
                            elif mode == "forgotten_favorites" and days > 180 and starred:
                                candidates.append(_format_song(s))
                        except ValueError:
                            pass # Skip if date parsing fails

        elif mode == "unheard_favorites":
            # 1. Fetch starred albums
            albums = _fetch_albums("starred", size=200)
            
            # 2. Randomize albums to inspect
            if albums:
                random.shuffle(albums)
                target_raw = fetch_limit * 2
                raw_candidates = []
                
                for alb in albums:
                    if len(raw_candidates) >= target_raw:
                        break
                    try:
                        songs_res = conn.getMusicDirectory(alb['id'])
                        songs = songs_res.get('directory', {}).get('child', [])
                        random.shuffle(songs)
                        for s in songs:
                            if not s.get('isDir') and s.get('playCount', 0) == 0:
                                raw_candidates.append(_format_song(s))
                    except:
                        continue
                
                # 3. Diversity Filter
                by_artist = {}
                for c in raw_candidates:
                    art = c['artist']
                    if art not in by_artist: by_artist[art] = []
                    by_artist[art].append(c)
                
                candidates = []
                artists = list(by_artist.keys())
                random.shuffle(artists)
                
                while len(candidates) < limit and artists:
                    for art in list(artists):
                        if len(candidates) >= limit: break
                        if by_artist[art]:
                            candidates.append(by_artist[art].pop(0))
                        else:
                            artists.remove(art)
                            
        elif mode == "divergent":
            # Logic from former get_divergent_recommendations
            freq = _fetch_albums("frequent", size=20)
            top_genres = {a.get('genre') for a in freq if a.get('genre')}
            all_genres = [g['value'] for g in conn.getGenres().get('genres', {}).get('genre', [])]
            divergent = list(set(all_genres) - top_genres)
            
            if not divergent:
                 return "No divergence found."
            
            random.shuffle(divergent)
            for g in divergent[:3]:
                res = conn.getRandomSongs(size=5, genre=g)
                if 'song' in res.get('randomSongs', {}):
                    candidates.extend([_format_song(s) for s in res['randomSongs']['song']])

        # --- 3. FILTERING ---
        filtered_candidates = []
        
        for cand in candidates:
            # Genre Filter
            genre_val = cand.get('genre', '').lower()
            if include_genres:
                if not any(incl.lower() in genre_val for incl in include_genres):
                    continue
            if exclude_genres:
                if any(excl.lower() in genre_val for excl in exclude_genres):
                    continue
                    
            # BPM Filter
            bpm_val = cand.get('bpm', 0)
            if min_bpm and bpm_val > 0:
                if bpm_val < min_bpm: continue
            if max_bpm and bpm_val > 0:
                if bpm_val > max_bpm: continue
                
            filtered_candidates.append(cand)
            
        candidates = filtered_candidates
        
        # --- 4. DIVERSITY & PAGINATION ---
        # Deduplicate by ID
        unique_candidates = {c['id']: c for c in candidates}
        candidates = list(unique_candidates.values())

        if mode not in ["most_played", "top_rated"]:
            random.shuffle(candidates)
            
        # Diversity Constraint (Max Tracks Per Artist)
        if max_tracks_per_artist:
            artist_counts = Counter()
            final_diversity_list = []
            for c in candidates:
                art = c.get('artist')
                if artist_counts[art] < max_tracks_per_artist:
                    final_diversity_list.append(c)
                    artist_counts[art] += 1
            candidates = final_diversity_list

        return json.dumps(candidates[:limit], indent=2)
    except Exception as e: 
        logger.error(f"Error in get_smart_candidates mode={mode}: {e}", exc_info=True)
        return str(e)



@mcp.tool()
@log_execution
def manage_playlist(name: str, operation: str = "get", track_ids: List[str] = None) -> str:
    """
    Manages playlists and moods.
    
    Args:
        name: Playlist name. For moods, use convention 'NG:Mood:{MoodName}'.
        operation: 
            - 'create': Replaces/Creates playlist with track_ids.
            - 'append': Adds track_ids to playlist (creates if missing).
            - 'get': Returns tracks in playlist.
        track_ids: List of track IDs (required for create/append).
    """
    conn = get_conn()
    try:
        # Find playlist by name
        playlists = conn.getPlaylists().get('playlists', {}).get('playlist', [])
        pl_id = next((p['id'] for p in playlists if p['name'] == name), None)
        
        if operation == "get":
            if not pl_id: return "[]"
            entries = conn.getPlaylist(pl_id).get('playlist', {}).get('entry', [])
            random.shuffle(entries)
            # Limit default return to 20 for safety
            return json.dumps([_format_song(s) for s in entries[:50]], indent=2)

        if operation == "delete":
            if not pl_id:
                return f"Playlist '{name}' not found."
            conn.deletePlaylist(pl_id)
            return f"Deleted playlist '{name}' (ID: {pl_id})."

        if not track_ids:
            return "Error: track_ids required for create/append."

        if operation == "create":
            if pl_id:
                # Subsonic API might allow duplicates, we enforce unique name by ID
                conn.deletePlaylist(pl_id)
                logger.info(f"Deleted existing playlist: {name} (ID: {pl_id})")
            
            conn.createPlaylist(name=name, songIds=track_ids)
            return f"Created playlist '{name}' with {len(track_ids)} tracks."

        elif operation == "append":
            if not pl_id:
                 conn.createPlaylist(name=name, songIds=track_ids)
                 return f"Created new playlist '{name}' with {len(track_ids)} tracks (append mode)."
            
            conn.updatePlaylist(pl_id, songIdsToAdd=track_ids)
            return f"Appended {len(track_ids)} tracks to '{name}'."
            
        return f"Unknown operation: {operation}"

    except Exception as e:
        logger.error(f"Error in manage_playlist {name}: {e}")
        return str(e)
@mcp.tool()
@log_execution
def assess_playlist_quality(song_ids: List[str]) -> str:
    """(Bliss) Checks diversity and repetition."""
    conn = get_conn()
    try:
        songs = [conn.getSong(sid).get('song') for sid in song_ids]
        songs = [s for s in songs if s]
        if not songs: return "No valid songs."
        
        artists = [s.get('artist') for s in songs]
        artist_counts = Counter(artists)
        most_common = artist_counts.most_common(1)[0] if artists else ("None", 0)
        
        return json.dumps({
            "total_tracks": len(songs),
            "unique_artists": len(set(artists)),
            "most_repetitive_artist": {
                "name": most_common[0],
                "count": most_common[1],
                "warning": most_common[1] > (len(songs) * 0.3)
            },
            "diversity_score": round(len(set(artists)) / len(songs), 2)
        }, indent=2)
    except Exception as e: return str(e)


@mcp.tool()
@log_execution
def search_music_enriched(query: str, limit: int = 20) -> str:
    """Standard search with full metadata."""
    conn = get_conn()
    search_response = conn.search3(query, songCount=limit)
    formatted_results = []
    
    search_results_container = search_response.get('searchResult3', {})
    if 'song' in search_results_container: 
        songs_list = search_results_container['song']
        # search3 can return a single dict instead of a list if only 1 result found in some versions,
        # but libsonic usually normalizes.
        if isinstance(songs_list, dict): 
            songs_list = [songs_list]
        formatted_results = [_format_song(s) for s in songs_list]
        
    return json.dumps(formatted_results, indent=2)


if __name__ == "__main__":
    mcp.run()