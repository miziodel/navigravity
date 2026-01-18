# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

__version__ = "0.1.7"

from mcp.server.fastmcp import FastMCP
import libsonic
import os
import sys
import json
import random
import datetime
from collections import Counter
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
import logging
from pythonjsonlogger import jsonlogger
import time
import functools
import re

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

def _fetch_search_results(query: str, song_count: int = 20, album_count: int = 0, artist_count: int = 0) -> Dict:
    """
    Abstractions for search3 to handle normalization and retries.
    """
    conn = get_conn()
    try:
        res = conn.search3(query, songCount=song_count, albumCount=album_count, artistCount=artist_count)
        data = res.get('searchResult3', {})
        
        # Normalize: ensure song/album/artist are lists even if single or empty
        for key in ['song', 'album', 'artist']:
            if key in data and not isinstance(data[key], list):
                data[key] = [data[key]]
            elif key not in data:
                data[key] = []
        
        # Fuzzy Fallback: if empty and contains special chars
        if not data.get('song') and not data.get('album') and not data.get('artist'):
            if "&" in query or " & " in query:
                fuzzy_query = query.replace("&", "").replace("  ", " ").strip()
                logger.info(f"Search empty. Retrying with fuzzy query: {fuzzy_query}")
                return _fetch_search_results(fuzzy_query, song_count, album_count, artist_count)
        
        return data
    except Exception as e:
        logger.error(f"Search failed for '{query}': {e}")
        return {"song": [], "album": [], "artist": []}


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
            return json.dumps({"result": f"Connected to Navidrome at {safe_url}"}, ensure_ascii=False)
        return json.dumps({"error": "Failed to connect to Navidrome (ping failed)"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to connect to Navidrome: {str(e)}"}, ensure_ascii=False)

@mcp.prompt()
def usage_guide() -> str:
    """Returns the 'Instruction Manual' for the Navigravity MCP server."""
    return """
    # Navigravity MCP Server Guide
    
    ## 1. Discovery
    - Start by checking `navidrome://info` (via `get_server_info`) to see server capabilities.
    - Use `check_connection` to verify the backend is up.
    - `search_music_enriched(query)`: Search for artists, albums, or songs.
    
    ## 2. Exploration
    - `get_genres()`: See what's available.
    - `explore_genre(genre)`: Deep dive into a genre.
    - `analyze_library(mode='taste_profile'|'composition'|'pillars')`: Understand the user's taste and library stats.
    - `get_similar_artists(artist_name)`: Find related artists (uses library data).
    - `get_similar_songs(song_id)`: Find related songs (Radio Mode).
    
    ## 3. Curation (The Quality First Workflow)
    Follow the Curator Manifesto:
    1. **Harvest**: Use `get_smart_candidates` with modes like 'divergent', 'hidden_gems', 'recently_added'.
    2. **Filter**: Use `assess_playlist_quality` (Crucial) and `batch_check_library_presence`.
    3. **Execute**: Use `manage_playlist` to create the final playlist.
    
    ## 4. Playback
    - This server primarily manages library state.
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

@mcp.tool()
@log_execution
def search_by_tag(tags: List[str], logic: str = "OR") -> str:
    """
    Multi-genre intersection/union for 'vibe' search.
    """
    all_results = []
    for tag in tags:
        # We use our new helper which handles retries and serialization
        results = _fetch_search_results(tag, song_count=100)
        all_results.append(set(s['id'] for s in results.get('song', [])))
    
    if not all_results:
        return json.dumps([])
        
    if logic.upper() == "AND":
        # Intersection
        final_ids = set.intersection(*all_results)
    else:
        # Union
        final_ids = set.union(*all_results)
        
    # Fetch full objects for the final IDs
    # Note: search3 doesn't support batch ID lookup, so we harvest from the initial results
    # To keep it efficient, we reconstruct from the first results gathered
    final_songs = []
    seen = set()
    
    # Re-run search or simple filter? 
    # For now, let's just do a union of all fetched songs and filter by final_ids
    pool = []
    for tag in tags:
        res = _fetch_search_results(tag, song_count=100)
        pool.extend(res.get('song', []))
        
    for s in pool:
        if s['id'] in final_ids and s['id'] not in seen:
            final_songs.append(_format_song(s))
            seen.add(s['id'])
            
    return json.dumps(final_songs, indent=2)

@mcp.tool()
@log_execution
def validate_playlist_rules(track_ids: List[str], rules: Dict) -> str:
    """
    Dry-run validation for diversity and mood.
    Example rules: {"max_tracks_per_artist": 2, "exclude_genres": ["Metal"], "min_bpm": 100}
    """
    conn = get_conn()
    violations = []
    artist_counts = Counter()
    
    max_per_artist = rules.get("max_tracks_per_artist")
    exclude_genres = [g.lower() for g in rules.get("exclude_genres", [])]
    min_bpm = rules.get("min_bpm")
    max_bpm = rules.get("max_bpm")

    for tid in track_ids:
        try:
            # Extract ID if it's a markdown link or has trailing chars
            clean_id = tid
            if "(" in tid and ")" in tid:
                match = re.search(r'\(([0-9a-f]{32})\)', tid)
                if match: clean_id = match.group(1)
            clean_id = clean_id.strip().strip(',')

            res = conn.getSong(clean_id)
            song = res.get('song')
            if not song:
                violations.append(f"Track {tid}: Not found in library.")
                continue
            
            # 1. Artist Diversity
            art = song.get('artist')
            artist_counts[art] += 1
            if max_per_artist and artist_counts[art] > max_per_artist:
                violations.append(f"Track '{song.get('title')}': Exceeds max per artist ({art}).")
            
            # 2. Genre Exclusion
            genre = song.get('genre', '').lower()
            if any(eg in genre for eg in exclude_genres):
                violations.append(f"Track '{song.get('title')}': Prohibited genre '{song.get('genre')}'.")
            
            # 3. BPM Range
            bpm = song.get('bpm', 0)
            if min_bpm and bpm > 0 and bpm < min_bpm:
                violations.append(f"Track '{song.get('title')}': BPM {bpm} is too low (target > {min_bpm}).")
            if max_bpm and bpm > max_bpm:
                violations.append(f"Track '{song.get('title')}': BPM {bpm} is too high (target < {max_bpm}).")

        except Exception as e:
            violations.append(f"Track {tid}: Error during validation - {str(e)}")

    return json.dumps({
        "is_valid": len(violations) == 0,
        "violations": violations,
        "summary": {
            "total_checked": len(track_ids),
            "unique_artists": len(artist_counts)
        }
    }, indent=2)

# --- TOOLS: DISCOVERY ---

@mcp.tool()
@log_execution
def get_genre_tracks(genre: Any, limit: int = 100) -> str:
    """
    Fetches random tracks for specific genre(s). 
    Accepts a single string or a list of strings.
    """
    conn = get_conn()
    genres = [genre] if isinstance(genre, str) else genre
    all_songs = []
    
    # Calculate limit per genre if multiple
    per_genre_limit = limit if len(genres) == 1 else (limit // len(genres)) + 1
    
    for g in genres:
        try:
            # Try getRandomSongs with genre filter
            res = conn.getRandomSongs(size=per_genre_limit, genre=g)
            songs = res.get('randomSongs', {}).get('song', [])
            
            if not songs:
                # Fallback
                res = conn.getSongsByGenre(g, count=per_genre_limit)
                songs = res.get('songsByGenre', {}).get('song', [])
                    
            all_songs.extend([_format_song(s) for s in songs])
        except Exception as e:
            logger.warning(f"Failed to fetch tracks for genre '{g}': {e}")
            
    # Deduplicate and shuffle
    unique_songs = {s['id']: s for s in all_songs}
    final_list = list(unique_songs.values())
    random.shuffle(final_list)
    
    return json.dumps(final_list[:limit], indent=2)


@mcp.tool()
@log_execution
def get_similar_artists(artist_id: Optional[str] = None, artist_name: Optional[str] = None, limit: int = 20) -> str:
    """
    Gets similar artists. Provide artist_id OR artist_name (name will be resolved to ID first).
    Uses getArtistInfo2 as a reliable fallback for library similarity.
    """
    conn = get_conn()
    try:
        target_id = artist_id
        
        # 1. Resolve Name if ID is missing
        if not target_id and artist_name:
            # Use artistCount=5 to allow for a more fuzzy match if needed, then filter
            search_res = conn.search3(artist_name, artistCount=5)
            artists = search_res.get('searchResult3', {}).get('artist', [])
            if not artists:
                return f"Error: Artist '{artist_name}' not found in library."
            
            # Use the first match (most relevant)
            target_id = artists[0].get('id')
            logger.info(f"Resolved artist '{artist_name}' to ID: {target_id}")

        if not target_id:
            return "Error: Either artist_id or artist_name must be provided."

        # 2. Tiered Discovery Logic
        similar_artists = []
        source_type = "canonical"

        # Attempt A: getSimilarArtists (Most direct)
        try:
             res = conn.getSimilarArtists(target_id, count=limit)
             similar_artists = res.get('similarArtists', {}).get('artist', [])
             if similar_artists: source_type = "canonical_similar"
        except Exception:
             pass
        
        # Attempt B: getArtistInfo2 (Secondary / Bio-based)
        if not similar_artists:
            try:
                res = conn.getArtistInfo2(target_id, count=limit)
                info = res.get('artistInfo2', {})
                similar_artists = info.get('similarArtist', [])
                if similar_artists: source_type = "canonical_info"
            except Exception:
                pass

        # Attempt C: Genre-Based Fallback
        if not similar_artists:
            try:
                # Need genre.
                genre = None
                # Fetch artist details to get genre
                art_info = conn.getArtist(target_id)
                genre = art_info.get('artist', {}).get('genre')

                if genre:
                    logger.info(f"No direct similar artists found. Falling back to genre: {genre}")
                    # Use _fetch_albums to find peers
                    genre_albums = _fetch_albums("byGenre", genre=genre, size=100)
                    
                    # Extract unique artists from these albums
                    peers = {}
                    for alb in genre_albums:
                        art = alb.get('artist')
                        art_id = alb.get('artistId')
                        if art_id != target_id and art:
                             if art_id not in peers:
                                 peers[art_id] = {'id': art_id, 'name': art, 'count': 0}
                             peers[art_id]['count'] += 1
                    
                    # Sort by frequency (proxy for relevance)
                    sorted_peers = sorted(peers.values(), key=lambda x: x['count'], reverse=True)[:limit]
                    
                    # Format as similar artists
                    similar_artists = sorted_peers 
                    source_type = "genre_fallback"
            except Exception as ex:
                 logger.error(f"Fallback failed: {ex}")

        output = []
        for a in similar_artists:
            output.append({
                "id": a.get('id'),
                "name": a.get('name'),
                "match": a.get('match') if 'match' in a else None,
                "source": source_type
            })
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in get_similar_artists: {e}")
        return str(e)


@mcp.tool()
@log_execution
def get_similar_songs(song_id: str, limit: int = 50) -> str:
    """Gets similar songs to the target song (Radio Mode)."""
    conn = get_conn()
    try:
        # getSimilarSongs2 returns songs from the library similar to query
        res = conn.getSimilarSongs2(song_id, count=limit)
        songs = res.get('similarSongs2', {}).get('song', [])
        
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
            # Fallback for album name: title is standard, but name/album are common in some versions/proxies
            alb_name = alb.get('title') or alb.get('name') or alb.get('album') or "Unknown Album"
            artist_stats[art]["albums"].append(alb_name)
            
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
    include_genres: Optional[List[str]] = None,
    exclude_genres: Optional[List[str]] = None,
    min_bpm: Optional[int] = None,
    max_bpm: Optional[int] = None,
    mood: Optional[str] = None,
    max_tracks_per_artist: Optional[int] = None
) -> str:
    """
    Generates lists based on stats with advanced filtering.
    
    Args:
        mode: recently_added, most_played, top_rated, lowest_rated, rediscover, rediscover_deep, 
              hidden_gems, unheard_favorites, divergent, fallen_pillars, similar_to_starred.
              Accepts comma-separated list of modes.
        limit: Max tracks to return (default 50)
        include_genres: List of genres to strictly include (case-insensitive partial match)
        exclude_genres: List of genres to exclude
        min_bpm: Minimum BPM
        max_bpm: Maximum BPM
        mood: 'relax', 'energy', 'focus', etc.
        max_tracks_per_artist: Diversity constraint
    """
    conn = get_conn()
    try:
        # --- 1. MOOD MAPPING ---
        if mood:
            mood = mood.lower()
            if mood == "relax":
                if max_bpm is None: max_bpm = 115
                if exclude_genres is None: exclude_genres = []
                exclude_genres.extend(["Metal", "Hard Rock", "Punk", "Industrial", "Techno", "Drum and Bass"])
            elif mood in ["energy", "workout"]:
                if min_bpm is None: min_bpm = 120
            elif mood == "focus":
                if exclude_genres is None: exclude_genres = []
                exclude_genres.extend(["Pop", "Hip-Hop", "Rap", "Vocal"])
                
        # --- 2. MULTI-MODE DISPATCH ---
        modes = [m.strip() for m in mode.split(",")]
        candidates = []
        today = datetime.datetime.now()

        for current_mode in modes:
            pool = []
            fetch_limit = limit * 2 if len(modes) > 1 else limit * 5
            if fetch_limit > 500: fetch_limit = 500

            if current_mode == "recently_added":
                albums = _fetch_albums("newest", size=fetch_limit)
                for alb in albums:
                    try:
                        res = conn.getMusicDirectory(alb['id'])
                        songs = [s for s in res.get('directory', {}).get('child', []) if not s.get('isDir')]
                        if songs: pool.append(_format_song(songs[0]))
                    except: continue

            elif current_mode == "most_played":
                frequent_albums = _fetch_albums("frequent", size=fetch_limit)
                for alb in frequent_albums:
                    try:
                        res = conn.getMusicDirectory(alb['id'])
                        pool.extend([_format_song(s) for s in res.get('directory', {}).get('child', []) if not s.get('isDir')])
                    except: continue
                pool.sort(key=lambda x: x.get('play_count', 0), reverse=True)

            elif current_mode == "top_rated":
                starred_res = conn.getStarred()
                if 'starred' in starred_res and 'song' in starred_res['starred']:
                    pool.extend([_format_song(s) for s in starred_res['starred']['song']])
                
                # Sample high rated
                random_pool = conn.getRandomSongs(size=fetch_limit)
                if 'randomSongs' in random_pool and 'song' in random_pool['randomSongs']:
                    pool.extend([_format_song(s) for s in random_pool['randomSongs']['song'] if s.get('userRating', 0) >= 3])

            elif current_mode == "rediscover": # V2: Album Archeology
                # Shift from random songs to random albums for better coherence
                alb_pool = _fetch_albums("random", size=20)
                for alb in alb_pool:
                     try:
                         res = conn.getMusicDirectory(alb['id'])
                         songs = [s for s in res.get('directory', {}).get('child', []) if not s.get('isDir')]
                         if songs:
                             # Pick a random track from the album
                             pool.append(_format_song(random.choice(songs)))
                     except: continue

            elif current_mode == "rediscover_deep":
                # Iterative random mining loop
                seen_ids = set()
                passes = 5
                for _ in range(passes):
                    if len(pool) >= limit: break
                    batch = conn.getRandomSongs(size=100)
                    if 'randomSongs' in batch and 'song' in batch['randomSongs']:
                        for s in batch['randomSongs']['song']:
                            lp_str = s.get('played')
                            if lp_str and s['id'] not in seen_ids:
                                lp_date = datetime.datetime.fromisoformat(lp_str.replace("Z", ""))
                                if (today - lp_date).days > 365:
                                    pool.append(_format_song(s))
                                    seen_ids.add(s['id'])

            elif current_mode == "hidden_gems":
                batch = conn.getRandomSongs(size=500)
                if 'randomSongs' in batch and 'song' in batch['randomSongs']:
                    pool.extend([_format_song(s) for s in batch['randomSongs']['song'] if s.get('playCount', 0) == 0])

            elif current_mode == "fallen_pillars":
                # Identify top artists and scan for forgotten tracks
                pillars = json.loads(analyze_library(mode="pillars"))[:10]
                for p in pillars:
                    try:
                        # getArtist returns albums, we need tracks
                        res = conn.getArtist(p['id'])
                        albums = res.get('artist', {}).get('album', [])
                        for alb in albums[:3]: # Scan top 3 albums
                            songs_res = conn.getMusicDirectory(alb['id'])
                            for s in songs_res.get('directory', {}).get('child', []):
                                if not s.get('isDir'):
                                    lp_str = s.get('played')
                                    if not lp_str or (today - datetime.datetime.fromisoformat(lp_str.replace("Z", ""))).days > 365:
                                        pool.append(_format_song(s))
                    except: continue

            elif current_mode == "similar_to_starred":
                starred = conn.getStarred()
                if 'starred' in starred and 'song' in starred['starred']:
                    seeds = random.sample(starred['starred']['song'], min(3, len(starred['starred']['song'])))
                    for seed in seeds:
                        try:
                            sim = conn.getSimilarSongs2(seed['id'], count=10)
                            pool.extend([_format_song(s) for s in sim.get('similarSongs2', {}).get('song', [])])
                        except: continue

            elif current_mode == "divergent":
                 # (Legacy divergent logic kept as fallback)
                 freq = _fetch_albums("frequent", size=10)
                 top_genres = {a.get('genre') for a in freq if a.get('genre')}
                 all_genres = [g['name'] for g in json.loads(get_genres())]
                 divergent = list(set(all_genres) - top_genres)
                 if divergent:
                     random.shuffle(divergent)
                     for g in divergent[:3]:
                         res = conn.getRandomSongs(size=5, genre=g)
                         if 'randomSongs' in res:
                             pool.extend([_format_song(s) for s in res['randomSongs'].get('song', [])])

            candidates.extend(pool)

        # --- 3. FILTERING & DIVERSITY ---
        unique_candidates = {c['id']: c for c in candidates}
        candidates = list(unique_candidates.values())
        
        filtered = []
        for c in candidates:
            # Genre
            gv = c.get('genre', '').lower()
            if include_genres and not any(i.lower() in gv for i in include_genres): continue
            if exclude_genres and any(e.lower() in gv for e in exclude_genres): continue
            # BPM
            bv = c.get('bpm', 0)
            if min_bpm and bv < min_bpm: continue
            if max_bpm and bv > 0 and bv > max_bpm: continue
            filtered.append(c)
            
        if not filtered and (mood or min_bpm):
            return "Error: Strict filtering eliminated all candidates. Try removing mood/BPM constraints."

        # Diversify
        if max_tracks_per_artist:
            counts = Counter()
            final = []
            for c in filtered:
                art = c['artist']
                if counts[art] < max_tracks_per_artist:
                    final.append(c)
                    counts[art] += 1
            filtered = final

        random.shuffle(filtered)
        return json.dumps(filtered[:limit], indent=2)

    except Exception as e:
        logger.error(f"get_smart_candidates failed: {e}", exc_info=True)
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
        songs = []
        warnings = []
        
        for sid_raw in song_ids:
            # logic: regex extracts the FIRST 32-char hex string found in the input
            match = re.search(r'([0-9a-fA-F]{32})', sid_raw)
            if not match:
                warnings.append(f"{sid_raw} (Invalid ID Format)")
                continue
            
            sid = match.group(1)
            try:
                res = conn.getSong(sid)
                s = res.get('song')
                if s: 
                    songs.append(s)
                else:
                    warnings.append(f"{sid} (Not found in library)")
            except Exception:
                warnings.append(sid)

        if not songs: 
            return json.dumps({"error": "No valid songs found", "warnings": warnings})
        
        artists = [s.get('artist') for s in songs]
        artist_counts = Counter(artists)
        most_common = artist_counts.most_common(1)[0] if artists else ("None", 0)
        
        result = {
            "total_tracks": len(songs),
            "unique_artists": len(set(artists)),
            "most_repetitive_artist": {
                "name": most_common[0],
                "count": most_common[1],
                "warning": most_common[1] > (len(songs) * 0.3)
            },
            "diversity_score": round(len(set(artists)) / len(songs), 2)
        }
        
        if warnings:
            result["warnings"] = warnings
            
        return json.dumps(result, indent=2)
    except Exception as e: return str(e)


@mcp.tool()
@log_execution
def search_music_enriched(query: str, limit: int = 20) -> str:
    """Standard search with full metadata."""
    results = _fetch_search_results(query, song_count=limit)
    formatted = [_format_song(s) for s in results.get('song', [])]
    return json.dumps(formatted, indent=2)


if __name__ == "__main__":
    mcp.run()