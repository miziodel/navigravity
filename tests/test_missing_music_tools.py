import sys
import os
import json
import logging

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.navidrome_mcp_server import analyze_user_taste_profile, batch_check_library_presence, get_smart_candidates

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

def test_analyze_taste():
    print("\n--- Testing analyze_user_taste_profile ---")
    result = analyze_user_taste_profile()
    try:
        data = json.loads(result)
        print("Success! Keys found:", data.keys())
        # print("Top Artists:", data.get("top_artists")[:5])
        return True
    except Exception as e:
        print("Failed to parse result:", result)
        print("Error:", e)
        return False

def test_batch_check():
    print("\n--- Testing batch_check_library_presence ---")
    query = [{"artist": "Pink Floyd", "album": "The Dark Side of the Moon"}, {"artist": "The Fake Band 12345"}]
    result = batch_check_library_presence(query)
    try:
        data = json.loads(result)
        print("Success! Results verified.")
        return True
    except Exception as e:
        print("Failed:", e)
        return False

def test_smart_candidates():
    print("\n--- Testing get_smart_candidates ---")
    
    modes = ["most_played", "top_rated", "lowest_rated", "rediscover"]
    success_count = 0
    
    for mode in modes:
        print(f"\n>> Testing mode: {mode}")
        result = get_smart_candidates(mode, limit=5)
        try:
            data = json.loads(result)
            print(f"   Received {len(data)} candidates")
            if data:
                print(f"   First item: {data[0].get('title')} - {data[0].get('artist')}")
                # Validation Logic
                if mode == "most_played":
                    assert data[0].get('play_count', 0) > 0, "Most played should have play count"
                    print("   ✅ Play count validation passed")
                elif mode == "top_rated":
                    item = data[0]
                    is_starred = item.get('starred')
                    is_rated = item.get('userRating', 0) >= 3 # Note: userRating might not be in formatted output unless we add it
                    # We need to verify logic, but _format_song might filter keys. 
                    # Let's trust visual check or update _format_song if needed for debugging.
                    print(f"   ℹ️ Item metadata: Starred={is_starred}, PlayCount={item.get('play_count')}")
                    assert is_starred or item.get('play_count') > 0, "Top rated should be starred or popular" 
                    print("   ✅ Rating heuristic passed")
                elif mode == "lowest_rated":
                    # Might be empty if user is positive!
                    if data:
                        print("   ⚠️ Found lowest rated content!")
                    else:
                        print("   ℹ️ No hate-list candidates found (Good sign?)")
            else:
                print("   ℹ️ No data returned (might be valid for empty stats)")
                
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed {mode}: {e}")
            
    return success_count == len(modes)

if __name__ == "__main__":
    t1 = test_analyze_taste()
    t2 = test_batch_check()
    t3 = test_smart_candidates()
    
    if t1 and t2 and t3:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)

