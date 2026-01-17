
# Script to verify smart candidates filtering logic
import sys
import os
import json
from unittest.mock import MagicMock

# Add src to path to import the server module
sys.path.append(os.path.abspath("src"))

# Mocking dependencies BEFORE import
sys.modules["libsonic"] = MagicMock()
sys.modules["mcp"] = MagicMock()
# Mocking dependencies BEFORE import
sys.modules["libsonic"] = MagicMock()
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()

# Setup FastMCP mock with pass-through decorators
mock_fastmcp_module = MagicMock()
mock_mcp_instance = MagicMock()

def pass_through_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

# If called as @mcp.tool without parens (unlikely here but good safety) or with parens
def tool_side_effect(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return pass_through_decorator()

mock_mcp_instance.tool.side_effect = tool_side_effect
mock_mcp_instance.resource.side_effect = tool_side_effect
mock_mcp_instance.prompt.side_effect = tool_side_effect

mock_fastmcp_module.FastMCP = MagicMock(return_value=mock_mcp_instance)
sys.modules["mcp.server.fastmcp"] = mock_fastmcp_module

sys.modules["pythonjsonlogger"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

# Set dummy environment variables to bypass the module-level check
os.environ["NAVIDROME_URL"] = "http://localhost:4533"
os.environ["NAVIDROME_USER"] = "dummy"
os.environ["NAVIDROME_PASS"] = "dummy"

# Now import the function to test
from navidrome_mcp_server import get_smart_candidates, get_conn

# Mock the connection object returned by get_conn
mock_conn = MagicMock()
# We need to patch get_conn to return our mock
import navidrome_mcp_server
navidrome_mcp_server.get_conn = lambda: mock_conn

def test_top_rated_with_mood_filtering():
    print("--- Testing top_rated with mood='energy' (min_bpm=120) ---")
    
    # Setup mock data for top_rated (which calls getStarred and getRandomSongs)
    # We'll use getRandomSongs mock for simplicity as top_rated uses it for pool
    mock_conn.getStarred.return_value = {} 
    
    # Mock pool with mixed BPMs
    mock_conn.getRandomSongs.return_value = {
        'randomSongs': {
            'song': [
                {'id': '1', 'title': 'High Energy', 'artist': 'A', 'bpm': 140, 'userRating': 4, 'playCount': 10},
                {'id': '2', 'title': 'Low Energy', 'artist': 'B', 'bpm': 80, 'userRating': 4, 'playCount': 10},
                {'id': '3', 'title': 'No BPM', 'artist': 'C', 'bpm': 0, 'userRating': 4, 'playCount': 10},
                {'id': '4', 'title': 'Comfortably Numb', 'artist': 'Pink Floyd', 'bpm': 0, 'userRating': 5, 'playCount': 100} 
            ]
        }
    }
    
    # Call with mood='energy' which sets min_bpm=120
    result = get_smart_candidates(mode="top_rated", mood="energy", limit=10)
    data = json.loads(result)
    
    print(f"Input Tracks: 4 (High Energy, Low Energy, No BPM, Comfortably Numb)")
    print(f"Output Tracks: {len(data)}")
    for t in data:
        print(f"- {t['title']} (BPM: {t['bpm']})")

    # Verification Logic
    has_low_energy = any(t['bpm'] > 0 and t['bpm'] < 120 for t in data)
    has_no_bpm = any(t['bpm'] == 0 for t in data)
    
    if has_low_energy:
        print("FAIL: Low energy tracks included!")
    elif has_no_bpm:
        print("WARN: Tracks with 0 BPM included (Loophole confirmed!)")
    else:
        print("SUCCESS: Only high energy tracks returned.")

if __name__ == "__main__":
    test_top_rated_with_mood_filtering()
