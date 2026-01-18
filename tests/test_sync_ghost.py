
import pytest
from unittest.mock import MagicMock, patch
import json
from src.navidrome_mcp_server import manage_playlist

@patch('src.navidrome_mcp_server.get_conn')
def test_manage_playlist_filters_ghost_ids(mock_get_conn):
    """
    TDD Test for Sync Ghost Bug.
    
    Scenario: User provides a list of IDs, some are valid, some are 'ghosts' (stale/invalid).
    
    Current Behavior (Bug): The system sends ALL IDs to Navidrome. Navidrome returns Success 
    but silently drops the ghost IDs.
    
    Desired Behavior (Fix): The system MUST verify IDs exist (via getSong) BEFORE sending 
    them to updatePlaylist. It should:
    1. Filter out the ghost ID.
    2. Only send the valid ID.
    3. Return a warning/info about the dropped ID.
    """
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn

    # Test Data
    valid_id = "valid_12345"
    ghost_id = "ghost_67890"
    playlist_id = "pl-test-1"
    playlist_name = "GhostBusters"

    # Mock: Playlist exists
    mock_conn.getPlaylists.return_value = {
        'playlists': {'playlist': [{'id': playlist_id, 'name': playlist_name}]}
    }

    # Mock: getSong behavior
    # - valid_id returns a song object
    # - ghost_id returns empty or raises error (simulating stale content)
    def side_effect_get_song(sid):
        if sid == valid_id:
            return {'song': {'id': valid_id, 'title': 'Valid Song', 'artist': 'Test'}}
        # Return empty for ghost to simulate not found
        return {} 
    
    mock_conn.getSong.side_effect = side_effect_get_song

    # --- EXECUTE ---
    # We attempt to append both IDs.
    result = manage_playlist(name=playlist_name, operation="append", track_ids=[valid_id, ghost_id])

    # --- VERIFY ---
    
    # 1. Verify that updatePlaylist was called
    assert mock_conn.updatePlaylist.called, "updatePlaylist should be called for valid tracks"
    
    # 2. Inspect the arguments passed to updatePlaylist
    # We expect ONLY valid_id to be passed.
    # The current code (buggy) will pass [valid_id, ghost_id].
    # The fixed code will pass [valid_id].
    
    call_args = mock_conn.updatePlaylist.call_args
    # call_args[1] is kwargs. Look for 'songIdsToAdd'
    added_ids = call_args[1].get('songIdsToAdd', [])
    
    # This assertion ensures we are NOT sending the ghost ID
    assert ghost_id not in added_ids, f"FAIL: Ghost ID {ghost_id} was sent to API! It should have been filtered."
    
    # This assertion ensures we ARE sending the valid ID
    assert valid_id in added_ids, "FAIL: Valid ID was not sent!"
    
    # 3. Verify that the result string contains some warning about the filtered track
    # (Optional but good UX)
    # assert "ghost_67890" in result # Warning about dropped track
