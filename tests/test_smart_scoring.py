import pytest
from src.navidrome_mcp_server import _calculate_smart_score

def test_smart_score_neutral():
    # No rating (0), No heart
    song = {"userRating": 0, "starred": False}
    assert _calculate_smart_score(song) == 3

def test_smart_score_stars_only():
    # 3 Stars, No heart
    song = {"userRating": 3, "starred": False}
    assert _calculate_smart_score(song) == 3 # (3 * 1) + 0 = 3? Wait, formula: (Stars * 1) + 5 if Heart else Base?
    # Re-reading plan:
    # "If userRating > 0 or starred: final_score = star_score + heart_bonus"
    # "Else: final_score = base_score (3)"
    
    # Correction based on exact formula in plan:
    # Star Score = 3. Heart Bonus = 0. Final = 3.
    # Logic check: User wants "Additive Scoring".
    # User's comment: "star -> 1 punti a stella"
    # So 3 stars should be 3 points?
    # But wait, Neutral (0 stars) is 3 points.
    # Does 1 star mean 1 point (worse than neutral)?
    # User comment: "no star/heart -> 3 punti", "star -> 1 punti a stella"
    # This implies 1 star = 1 point. 2 stars = 2 points. 3 stars = 3 points.
    # So a 1-star song is WORSE than a neutral song? Correct, usually 1 star is "bad".
    
    # Case: 4 stars. Score = 4.
    song_4 = {"userRating": 4, "starred": False}
    assert _calculate_smart_score(song_4) == 4

def test_smart_score_heart_only():
    # 0 Stars, Heart
    song = {"userRating": 0, "starred": True}
    # Heart bonus = 5.
    # Metric: if userRating > 0 or starred.
    # Star score = 0.
    # Final = 0 + 5 = 5.
    assert _calculate_smart_score(song) == 5

def test_smart_score_combined():
    # 4 Stars + Heart
    song = {"userRating": 4, "starred": True}
    # Star score = 4. Heart bonus = 5.
    # Final = 4 + 5 = 9.
    assert _calculate_smart_score(song) == 9

def test_smart_score_max():
    # 5 Stars + Heart
    song = {"userRating": 5, "starred": True}
    # Final = 5 + 5 = 10.
    assert _calculate_smart_score(song) == 10
