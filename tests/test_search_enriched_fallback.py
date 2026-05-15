# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT
#
# TDD: test_search_enriched_fallback.py
# Red phase for search_music_enriched v0.2.0 multi-strategy fallback.
# All tests here must FAIL before implementation and PASS after.
#
# Plan: implementation_plan.md (approved 2026-05-15)

import pytest
import json
from unittest.mock import MagicMock, call
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

# Mock heavy dependencies BEFORE import (same pattern as test_v0_1_7_fixes.py)
sys.modules["libsonic"] = MagicMock()
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()
sys.modules["pythonjsonlogger"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# FastMCP decorator pass-through (required for module import to succeed)
mcp_mock = MagicMock()

def _tool_side_effect(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    def decorator(func):
        return func
    return decorator

mcp_mock.tool.side_effect = _tool_side_effect
mcp_mock.resource.side_effect = _tool_side_effect
mcp_mock.prompt.side_effect = _tool_side_effect

fastmcp_module_mock = MagicMock()
fastmcp_module_mock.FastMCP = MagicMock(return_value=mcp_mock)
sys.modules["mcp.server.fastmcp"] = fastmcp_module_mock

# Dummy env vars to bypass module-level connection setup
os.environ["NAVIDROME_URL"] = "http://localhost:4533"
os.environ["NAVIDROME_USER"] = "dummy"
os.environ["NAVIDROME_PASS"] = "dummy"

from navidrome_mcp_server import search_music_enriched


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_song(track_id="a" * 32, title="Test Song", artist="Test Artist",
               album="Test Album", genre="Jazz"):
    """Helper: minimal song dict matching Navidrome search3 response format."""
    return {
        "id": track_id,
        "title": title,
        "artist": artist,
        "artistId": "art_" + track_id,
        "album": album,
        "albumId": "alb_" + track_id,
        "genre": genre,
        "duration": 300,
        "year": 2000,
        "playCount": 0,
        "userRating": 0,
        "starred": None,
        "bpm": 0,
        "path": f"/music/{artist}/{album}/{title}.flac",
        "comment": "",
    }

def _make_album(album_id, title, artist):
    """Helper: minimal album dict matching search3 album result."""
    return {"id": album_id, "title": title, "artist": artist}

def _make_directory_response(songs):
    """Helper: wrap song list in getMusicDirectory response format."""
    return {"directory": {"child": songs}}

def _empty_search():
    return {"searchResult3": {"song": [], "album": [], "artist": []}}

def _song_search(songs):
    return {"searchResult3": {"song": songs, "album": [], "artist": []}}

def _album_search(albums):
    return {"searchResult3": {"song": [], "album": albums, "artist": []}}


# ---------------------------------------------------------------------------
# T1 — Compound query with album expansion (core fix)
# ---------------------------------------------------------------------------

def test_t1_compound_query_falls_back_via_album_expansion(mock_conn):
    """
    T1: Query "Pharaoh's Dance Miles Davis" returns [] from song search,
    but search3 finds album "Bitches Brew". Tool must expand album into tracks.
    """
    target_song = _make_song(
        track_id="b" * 32,
        title="Pharaoh's Dance",
        artist="Miles Davis",
        album="Bitches Brew",
    )
    target_album = _make_album("alb_bitches_brew", "Bitches Brew", "Miles Davis")

    def search_side_effect(query, **kwargs):
        # First call: compound query → only album found
        if "Pharaoh" in query or "Miles" in query:
            return {"searchResult3": {"song": [], "album": [target_album], "artist": []}}
        return _empty_search()

    mock_conn.search3.side_effect = search_side_effect
    mock_conn.getMusicDirectory.return_value = _make_directory_response([target_song])

    result = search_music_enriched("Pharaoh's Dance Miles Davis")
    data = json.loads(result)

    assert isinstance(data, list), "Must return a JSON list"
    assert len(data) >= 1, "Must find at least one track via album expansion"
    assert data[0]["title"] == "Pharaoh's Dance"
    mock_conn.getMusicDirectory.assert_called_once_with("alb_bitches_brew")


# ---------------------------------------------------------------------------
# T2 — "Artist AlbumName" format: filter on song['album'], not song['title']
# ---------------------------------------------------------------------------

def test_t2_artist_albumname_format_filters_on_album_field_not_title(mock_conn):
    """
    T2: Query "Daft Punk Discovery" → song search empty, album "Discovery" found.
    Expanded tracks have title != "Discovery". Must still return them (album expansion,
    NOT title filtering).
    """
    track1 = _make_song("c" * 32, title="One More Time", artist="Daft Punk", album="Discovery")
    track2 = _make_song("d" * 32, title="Harder Better Faster Stronger", artist="Daft Punk", album="Discovery")
    target_album = _make_album("alb_discovery", "Discovery", "Daft Punk")

    mock_conn.search3.return_value = {"searchResult3": {
        "song": [], "album": [target_album], "artist": []
    }}
    mock_conn.getMusicDirectory.return_value = _make_directory_response([track1, track2])

    result = search_music_enriched("Daft Punk Discovery")
    data = json.loads(result)

    assert isinstance(data, list)
    assert len(data) == 2, "Must return both tracks from expanded album"
    titles = [t["title"] for t in data]
    assert "One More Time" in titles
    assert "Harder Better Faster Stronger" in titles


# ---------------------------------------------------------------------------
# T3 — `artist` parameter filters on song['artist'], not title
# ---------------------------------------------------------------------------

def test_t3_artist_param_filters_on_artist_field(mock_conn):
    """
    T3: `artist="Miles Davis"` → post-filter keeps only songs where
    song['artist'] contains "miles davis" (case-insensitive).
    """
    song_match = _make_song("e" * 32, title="Kind of Blue Track", artist="Miles Davis", album="Kind of Blue")
    song_other = _make_song("f" * 32, title="Another Track", artist="John Coltrane", album="Kind of Blue")

    mock_conn.search3.return_value = _song_search([song_match, song_other])

    result = search_music_enriched("Kind of Blue", artist="Miles Davis")
    data = json.loads(result)

    assert all(d["artist"] == "Miles Davis" for d in data), \
        "Post-filter on artist must exclude non-matching artists"
    assert any(d["title"] == "Kind of Blue Track" for d in data)
    assert not any(d["artist"] == "John Coltrane" for d in data)


# ---------------------------------------------------------------------------
# T4 — `album` parameter filters on song['album'], NOT on song['title']
# ---------------------------------------------------------------------------

def test_t4_album_param_filters_on_album_field_not_title(mock_conn):
    """
    T4: `album="Bitches Brew"` must filter on song['album'], not song['title'].
    A song titled "Pharaoh's Dance" from album "Bitches Brew" must PASS.
    A song titled "Bitches Brew" from album "Other Album" must FAIL.
    """
    song_correct = _make_song("g" * 32, title="Pharaoh's Dance", artist="Miles Davis", album="Bitches Brew")
    song_wrong = _make_song("h" * 32, title="Bitches Brew", artist="Miles Davis", album="Other Album")

    mock_conn.search3.return_value = _song_search([song_correct, song_wrong])

    result = search_music_enriched("Miles Davis", album="Bitches Brew")
    data = json.loads(result)

    assert any(d["title"] == "Pharaoh's Dance" for d in data), \
        "Song from album 'Bitches Brew' must be included even if title != 'Bitches Brew'"
    assert not any(d["album"] == "Other Album" for d in data), \
        "Song NOT in album 'Bitches Brew' must be excluded"


# ---------------------------------------------------------------------------
# T5 — Post-filter is case-insensitive
# ---------------------------------------------------------------------------

def test_t5_post_filter_is_case_insensitive(mock_conn):
    """
    T5: `artist="miles davis"` (lowercase) must match song['artist']="Miles Davis".
    """
    song = _make_song("i" * 32, title="Flamenco Sketches", artist="Miles Davis", album="Kind of Blue")
    mock_conn.search3.return_value = _song_search([song])

    result = search_music_enriched("Kind of Blue", artist="miles davis")
    data = json.loads(result)

    assert len(data) >= 1
    assert data[0]["artist"] == "Miles Davis"


# ---------------------------------------------------------------------------
# T6 — Raw fallback: never return [] if tracks exist
# ---------------------------------------------------------------------------

def test_t6_raw_fallback_never_returns_empty(mock_conn):
    """
    T6: All strategies (step 1-4) return empty. Step 5 raw fallback must
    still attempt the original query and return whatever search3 gives.
    The tool must NEVER raise an exception.
    """
    fallback_song = _make_song("j" * 32, title="Fallback Track", artist="Unknown", album="Unknown")
    call_count = {"n": 0}

    def search_side_effect(query, **kwargs):
        call_count["n"] += 1
        # Last call (raw fallback) returns a result
        if call_count["n"] >= 2:
            return _song_search([fallback_song])
        return _empty_search()

    mock_conn.search3.side_effect = search_side_effect
    mock_conn.getMusicDirectory.return_value = _make_directory_response([])

    result = search_music_enriched("zzz_nonexistent_query_xyz")

    # Must not raise
    assert isinstance(result, str)
    data = json.loads(result)
    assert isinstance(data, list)  # Always a list, never an error string for this tool


# ---------------------------------------------------------------------------
# T7 — Backward compatibility: no artist/album params → same as v0.1.9
# ---------------------------------------------------------------------------

def test_t7_backward_compatible_single_query(mock_conn):
    """
    T7: `search_music_enriched("jazz")` with NO artist/album params
    must behave identically to v0.1.9 (simple search3 call, return songs).
    """
    song = _make_song("k" * 32, title="Blue in Green", artist="Miles Davis", album="Kind of Blue")
    mock_conn.search3.return_value = _song_search([song])

    result = search_music_enriched("jazz")
    data = json.loads(result)

    assert isinstance(data, list)
    assert len(data) == 1
    # search3 called exactly once for simple query (no fallback needed)
    mock_conn.search3.assert_called_once()


# ---------------------------------------------------------------------------
# T8 — Album expansion is capped at 2 albums
# ---------------------------------------------------------------------------

def test_t8_album_expansion_capped_at_two(mock_conn):
    """
    T8: If search3 returns 5 albums, getMusicDirectory must be called
    at most 2 times (latency cap from architecture decision D4).
    """
    albums = [_make_album(f"alb_{i}", f"Album {i}", "Artist") for i in range(5)]
    song = _make_song("l" * 32, title="Track", artist="Artist", album="Album 0")

    mock_conn.search3.return_value = {"searchResult3": {
        "song": [], "album": albums, "artist": []
    }}
    mock_conn.getMusicDirectory.return_value = _make_directory_response([song])

    search_music_enriched("Artist", limit=20)

    assert mock_conn.getMusicDirectory.call_count <= 2, \
        f"getMusicDirectory called {mock_conn.getMusicDirectory.call_count} times, expected <= 2"


# ---------------------------------------------------------------------------
# T9 — Unicode normalization is a step-4 fallback (not step 1)
# ---------------------------------------------------------------------------

def test_t9_unicode_normalization_is_step4_fallback(mock_conn):
    """
    T9: Query "Désordre" → step 1 fails → step 4 retries with "Desordre"
    (NFKD normalized). search3 must be called with normalized query in retry.
    """
    normalized_song = _make_song(
        "m" * 32,
        title="Désordre",
        artist="Ligeti",
        album="Piano Études",
    )
    calls = []

    def search_side_effect(query, **kwargs):
        calls.append(query)
        if "Desordre" in query or "desordre" in query.lower():
            return _song_search([normalized_song])
        return _empty_search()

    mock_conn.search3.side_effect = search_side_effect
    mock_conn.getMusicDirectory.return_value = _make_directory_response([])

    result = search_music_enriched("Désordre")
    data = json.loads(result)

    # Step 1 called first with original query
    assert any("Désordre" in c or "D" in c for c in calls), \
        "Original query must be tried first"
    # Step 4 must have triggered a normalized retry
    normalized_calls = [c for c in calls if "Desordre" in c]
    assert len(normalized_calls) >= 1, \
        "Unicode normalization fallback (step 4) must retry with NFKD query"
    assert len(data) >= 1, "Normalized query must find the track"


# ---------------------------------------------------------------------------
# T10 — Unicode normalization: no loop if query already ASCII
# ---------------------------------------------------------------------------

def test_t10_unicode_normalization_no_loop_for_ascii_query(mock_conn):
    """
    T10: Query "Jazz Piano" (already ASCII) → normalization produces identical
    string → step 4 must NOT trigger an additional call (infinite loop guard).
    """
    song = _make_song("n" * 32, title="Jazz Piano Track", artist="Bill Evans", album="Sunday")
    mock_conn.search3.return_value = _song_search([song])

    result = search_music_enriched("Jazz Piano")
    data = json.loads(result)

    # Step 1 succeeds → no normalization fallback triggered
    # search3 called exactly once
    assert mock_conn.search3.call_count == 1, \
        f"For ASCII query, search3 must be called once. Got {mock_conn.search3.call_count}"
    assert len(data) == 1
