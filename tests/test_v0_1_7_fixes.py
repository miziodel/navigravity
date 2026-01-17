
# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

import pytest
import json
from unittest.mock import MagicMock, call
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath("src"))

# Mock dependencies BEFORE import
sys.modules["libsonic"] = MagicMock()
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()
sys.modules["pythonjsonlogger"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# Setup FastMCP mock to handle decorators (simplistic pass-through)
mcp_mock = MagicMock()
def tool_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
# Handle @mcp.tool() and @mcp.tool usage
def tool_side_effect(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return tool_decorator()

mcp_mock.tool.side_effect = tool_side_effect
mcp_mock.resource.side_effect = tool_side_effect
mcp_mock.prompt.side_effect = tool_side_effect

# Mock FastMCP constructor to return our mcp_mock
fastmcp_module_mock = MagicMock()
fastmcp_module_mock.FastMCP = MagicMock(return_value=mcp_mock)
sys.modules["mcp.server.fastmcp"] = fastmcp_module_mock

# Set dummy environment variables to bypass the module-level check
os.environ["NAVIDROME_URL"] = "http://localhost:4533"
os.environ["NAVIDROME_USER"] = "dummy"
os.environ["NAVIDROME_PASS"] = "dummy"

# Now import the actual functions.
from navidrome_mcp_server import assess_playlist_quality, get_smart_candidates, search_music_enriched

def test_assess_quality_valid_ids(mock_conn):
    """Test standard success case to ensure regression safety."""
    # Mocking getSong side effect for valid IDs
    def get_song_side_effect(id):
        return {'song': {'id': id, 'artist': 'Artist A', 'title': f'Song {id}'}}
    mock_conn.getSong.side_effect = get_song_side_effect

    result = assess_playlist_quality(["1", "2"])
    data = json.loads(result)
    
    assert data['total_tracks'] == 2
    assert 'warnings' not in data or not data['warnings']

def test_assess_quality_partial_failure_ghost_ids(mock_conn):
    """
    TDD: Test fix for 'Ghost IDs'. 
    If a song ID is missing (returns None or empty), it should be skipped with a warning,
    not crash or return error string.
    """
    def get_song_side_effect(id):
        if id == "ghost": return {} # Simulates Navidrome "not found" or empty response
        return {'song': {'id': id, 'artist': 'Valid Artist', 'title': 'Valid Song'}}
    
    mock_conn.getSong.side_effect = get_song_side_effect

    # Call with 2 valid and 1 ghost
    result = assess_playlist_quality(["1", "ghost", "2"])
    data = json.loads(result)

    # Logic: Should calculate stats on the 2 valid songs
    assert data['total_tracks'] == 2 # Only valid ones count for stats
    assert 'warnings' in data
    assert "ghost" in data['warnings']
    assert data['diversity_score'] == 0.5 # 1 artist / 2 songs = 0.5

def test_strict_params_bpm_loophole(mock_conn):
    """
    TDD: Test fix for BPM Loophole.
    Tracks with BPM=0 should be excluded if min_bpm is set.
    """
    # Setup mock for get_smart_candidates -> top_rated
    # Logic uses getStarred and getRandomSongs. We'll mock getRandomSongs pool.
    mock_conn.getStarred.return_value = {}
    mock_conn.getRandomSongs.return_value = {
        'randomSongs': {
            'song': [
               {'id': '1', 'title': 'High Energy', 'artist': 'A', 'bpm': 140, 'userRating': 4, 'playCount': 10},
               {'id': '2', 'title': 'No BPM', 'artist': 'B', 'bpm': 0, 'userRating': 4, 'playCount': 10}
            ]
        }
    }

    # Request Energy (min_bpm=120 internal default or explicit)
    # mood='energy' -> min_bpm=120
    result_json = get_smart_candidates(mode="top_rated", mood="energy", limit=10)
    
    # We expect result to be a JSON list containing ONLY High Energy
    data = json.loads(result_json)
    assert len(data) == 1
    assert data[0]['title'] == "High Energy"
    # Ensure No BPM is gone
    assert not any(d['title'] == "No BPM" for d in data)

def test_strict_params_fail_fast_if_empty(mock_conn):
    """
    TDD: Test "Error String" return if strict filtering eliminates all candidates.
    Behavioral Change: Don't return [], return "Error: ..."
    """
    mock_conn.getStarred.return_value = {}
    mock_conn.getRandomSongs.return_value = {
        'randomSongs': {
            'song': [
               {'id': '2', 'title': 'No BPM', 'artist': 'B', 'bpm': 0, 'userRating': 4}
            ]
        }
    }

    result = get_smart_candidates(mode="top_rated", mood="energy", limit=10)
    
    # Expecting an error string, NOT JSON
    # This might look like a JSON string if we decide to return {"error": ...}, 
    # but the plan said "ERROR STRING instead of a result list".
    # Let's assume it returns a raw string starting with "Error" or "Warning".
    
    # If it returns valid JSON [], the test fails (current behavior)
    assert isinstance(result, str)
    assert "0 matches found" in result or "strict" in result.lower() or "error" in result.lower()
    # Ensure it's NOT a json list of empty results
    if result.strip().startswith("["):
        assert result == "[]" and "Should return error/warning string, not empty list" == ""

def test_search_fallback_mechanism(mock_conn):
    """
    TDD: Test Search Reliability.
    If exact search fails, retry with fallback logic.
    """
    # Scenario: " Artist A & B " -> Search 1: Strict -> []
    # Fallback -> Search 2: " Artist A B " or " Artist A " -> [Result]
    
    # We'll rely on the simple fallback: if first search empty, maybe try broader? 
    # Plan says: "Fuzzy Fallback... try conn.search3(query, audio=False)?"
    # Or replace "&".
    
    # Let's mock side_effect for search3
    def search_side_effect(query, **kwargs):
        if query == "Simon & Garfunkel":
            return {'searchResult3': {'song': []}} # Empty
        if query == "Simon Garfunkel": # Fallback query
             return {'searchResult3': {'song': [{'id': '1', 'title': 'Mrs. Robinson', 'artist': 'Simon & Garfunkel'}]}}
        return {'searchResult3': {}}

    mock_conn.search3.side_effect = search_side_effect

    # We assume the implementation will try replacing "&" with " " or similar strategy
    # If we just want to test "any fallback", we can check call_args_list
    
    # NOTE: Since we haven't defined the exact fuzzy logic in code yet, 
    # let's assume the implementation will try to sanitize the query if it contains "&"
    
    result = search_music_enriched("Simon & Garfunkel")
    data = json.loads(result)
    
    # Verify we got results eventually
    assert len(data) == 1
    assert data[0]['title'] == "Mrs. Robinson"
    
    # Verify search3 was called twice or with modified query
    assert mock_conn.search3.call_count >= 1
    # Check if a fallback call happened (implementation detail)
