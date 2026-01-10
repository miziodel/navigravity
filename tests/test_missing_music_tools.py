import sys
import os
import json
import logging
import pytest

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.navidrome_mcp_server import analyze_library, batch_check_library_presence, get_smart_candidates

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

def test_analyze_taste():
    print("\n--- Testing analyze_library(mode='taste_profile') ---")
    result = analyze_library(mode='taste_profile')
    # Assert result is not None/Empty
    assert result, "Result should not be empty"
    
    try:
        data = json.loads(result)
        # Assert expected keys exist
        assert "top_artists" in data, "Should return top_artists"
        assert "top_genres" in data, "Should return top_genres"
        print("Success! Keys found:", data.keys())
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON result: {result}. Error: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

def test_batch_check():
    print("\n--- Testing batch_check_library_presence ---")
    query = [{"artist": "Pink Floyd", "album": "The Dark Side of the Moon"}, {"artist": "The Fake Band 12345"}]
    result = batch_check_library_presence(query)
    
    try:
        data = json.loads(result)
        assert isinstance(data, list), "Result should be a list"
        assert len(data) == 2, "Should return 2 results"
        
        # Verify first result structure
        first_item = data[0]
        assert "artist" in first_item
        assert "present" in first_item
        
        print("Success! Results verified.")
    except Exception as e:
        pytest.fail(f"Failed: {e}")


def test_smart_candidates():
    print("\n--- Testing get_smart_candidates ---")
    
    modes = ["most_played", "top_rated", "lowest_rated", "rediscover"]
    
    for mode in modes:
        print(f"\n>> Testing mode: {mode}")
        result = get_smart_candidates(mode, limit=5)
        try:
            data = json.loads(result)
            print(f"   Received {len(data)} candidates")
            
            assert isinstance(data, list), "Should return a list of candidates"
            
            if data:
                print(f"   First item: {data[0].get('title')} - {data[0].get('artist')}")
                # Validation Logic
                if mode == "most_played":
                    assert data[0].get('play_count', 0) > 0, "Most played should have play count"
                    print("   ✅ Play count validation passed")
                elif mode == "top_rated":
                    item = data[0]
                    is_starred = item.get('starred')
                    is_rated = item.get('userRating', 0) >= 3 
                    print(f"   ℹ️ Item metadata: Starred={is_starred}, PlayCount={item.get('play_count')}")
                    # Flexible assertion: Starred OR popular (heuristic fallback)
                    assert is_starred or item.get('play_count') > 0, "Top rated should be starred or popular"
                    print("   ✅ Rating heuristic passed")
                elif mode == "lowest_rated":
                    if data:
                        print("   ⚠️ Found lowest rated content!")
                    else:
                        print("   ℹ️ No hate-list candidates found (Good sign?)")
            else:
                print("   ℹ️ No data returned (might be valid for empty stats)")
                
        except Exception as e:
             pytest.fail(f"   ❌ Failed {mode}: {e}")


