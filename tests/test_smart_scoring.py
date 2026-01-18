import pytest
from src.navidrome_mcp_server import _calculate_smart_score

def test_smart_score_neutral():
    # No rating (0), No heart
    song = {"rating": 0, "starred": False}
    assert _calculate_smart_score(song) == 3

def test_smart_score_stars_only():
    # 3 Stars, No heart
    song = {"rating": 3, "starred": False}
    assert _calculate_smart_score(song) == 3 # (3 * 1) + 0 = 3? Wait, formula: (Stars * 1) + 5 if Heart else Base?
    # Re-reading plan:
    # "If rating > 0 or starred: final_score = star_score + heart_bonus"
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
    song_4 = {"rating": 4, "starred": False}
    assert _calculate_smart_score(song_4) == 4

def test_smart_score_heart_only():
    # 0 Stars, Heart
    song = {"rating": 0, "starred": True}
    # Heart bonus = 5.
    # Metric: if rating > 0 or starred.
    # Star score = 0.
    # Final = 0 + 5 = 5.
    assert _calculate_smart_score(song) == 5

def test_smart_score_combined():
    # 4 Stars + Heart
    song = {"rating": 4, "starred": True}
    # Star score = 4. Heart bonus = 5.
    # Final = 4 + 5 = 9.
    assert _calculate_smart_score(song) == 9

def test_smart_score_max():
    # 5 Stars + Heart
    song = {"rating": 5, "starred": True}
    # Final = 5 + 5 = 10.
    assert _calculate_smart_score(song) == 10

def test_smart_score_one_star():
    # 1 Star, No heart - Below neutral threshold
    song = {"rating": 1, "starred": False}
    # User confirmed: 1 star means we've expressed opinion (worse than neutral)
    # Star score = 1. Heart bonus = 0. Final = 1.
    assert _calculate_smart_score(song) == 1

def test_smart_score_two_stars():
    # 2 Stars, No heart - Still below neutral threshold
    song = {"rating": 2, "starred": False}
    # Star score = 2. Heart bonus = 0. Final = 2.
    assert _calculate_smart_score(song) == 2

def test_smart_score_one_star_with_heart():
    # Edge case: Low rating but hearted (conflicting signals)
    song = {"rating": 1, "starred": True}
    # Star score = 1. Heart bonus = 5. Final = 1 + 5 = 6.
    assert _calculate_smart_score(song) == 6
