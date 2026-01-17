
# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

import pytest
import json
from unittest.mock import MagicMock
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

# Setup FastMCP mock
mcp_mock = MagicMock()
def tool_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
def tool_side_effect(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return tool_decorator()

mcp_mock.tool.side_effect = tool_side_effect
mcp_mock.resource.side_effect = tool_side_effect
mcp_mock.prompt.side_effect = tool_side_effect

fastmcp_module_mock = MagicMock()
fastmcp_module_mock.FastMCP = MagicMock(return_value=mcp_mock)
sys.modules["mcp.server.fastmcp"] = fastmcp_module_mock

# Set dummy environment variables
os.environ["NAVIDROME_URL"] = "http://localhost:4533"
os.environ["NAVIDROME_USER"] = "dummy"
os.environ["NAVIDROME_PASS"] = "dummy"

# Import server functions (will fail if implementation doesn't exist yet, which is good for TDD)
try:
    from navidrome_mcp_server import get_similar_artists, get_similar_songs
except ImportError:
    # If generic import fails, we might need to mock them if they don't exist yet
    # But strictly TDD means we write the test expecting them to exist.
    pass

def test_get_similar_artists(mock_conn):
    """Test get_similar_artists tool wrapper."""
    # Mock response from libsonic
    mock_conn.getSimilarArtists.return_value = {
        'similarArtists': {
            'artist': [
                {'id': '2', 'name': 'Pink Floyd', 'match': 0.9},
                {'id': '3', 'name': 'Genesis', 'match': 0.8}
            ]
        }
    }

    # Call the tool (assuming it's imported or we'll import it)
    from navidrome_mcp_server import get_similar_artists
    result = get_similar_artists(artist_id="1", limit=5)
    
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]['name'] == 'Pink Floyd'
    assert data[0]['match'] == 0.9 # Pass-through value
    
    # Verify call to libsonic
    mock_conn.getSimilarArtists.assert_called_with("1", count=5)


def test_get_similar_songs(mock_conn):
    """Test get_similar_songs tool wrapper."""
    # Mock response from libsonic using getSimilarSongs2 (which usually returns random-ish similar songs)
    mock_conn.getSimilarSongs2.return_value = {
        'similarSongs2': {
            'song': [
                {'id': '10', 'title': 'Time', 'artist': 'Pink Floyd', 'album': 'DSOTM'},
                {'id': '11', 'title': 'Money', 'artist': 'Pink Floyd', 'album': 'DSOTM'}
            ]
        }
    }

    from navidrome_mcp_server import get_similar_songs
    result = get_similar_songs(song_id="100", limit=10)
    
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]['title'] == 'Time'
    
    # Verify call
    mock_conn.getSimilarSongs2.assert_called_with("100", count=10)
