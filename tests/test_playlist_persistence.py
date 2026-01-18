
import pytest
from unittest.mock import MagicMock, patch, call
from src.navidrome_mcp_server import manage_playlist

@patch('src.navidrome_mcp_server.get_conn')
def test_playlist_batching_create(mock_get_conn):
    """
    Verifies that manage_playlist batches large requests.
    Scenario: Creating a playlist with 35 tracks.
    Expected:
    - 1 call to createPlaylist with 10 tracks.
    - 1 call to updatePlaylist with 10 tracks.
    - 1 call to updatePlaylist with 10 tracks.
    - 1 call to updatePlaylist with 5 tracks.
    """
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn
    
    # Mock getPlaylists to return empty first, then return the created playlist
    mock_conn.getPlaylists.side_effect = [
        {'playlists': {'playlist': []}}, # Initial check (not found)
        {'playlists': {'playlist': [{'id': 'new-pl-id', 'name': 'BatchTest'}]}} # After creation
    ]
    
    # Setup 35 fake IDs
    track_ids = [f"id-{i}" for i in range(35)]
    
    result = manage_playlist(name="BatchTest", operation="create", track_ids=track_ids)
    
    # Verification
    assert "Created playlist 'BatchTest'" in result
    
    # Check calls
    # 1. createPlaylist should be called once with the first 10
    mock_conn.createPlaylist.assert_called_once()
    create_call = mock_conn.createPlaylist.call_args
    assert create_call.kwargs['name'] == "BatchTest"
    assert len(create_call.kwargs['songIds']) == 10
    assert create_call.kwargs['songIds'] == track_ids[:10]
    
    # 2. updatePlaylist should be called 3 times (for the remaining 25 tracks: 10, 10, 5)
    assert mock_conn.updatePlaylist.call_count == 3
    
    # Check that updatePlaylist was called with the correct ID
    update_calls = mock_conn.updatePlaylist.call_args_list
    for call_args in update_calls:
        assert call_args[0][0] == 'new-pl-id'

@patch('src.navidrome_mcp_server.get_conn')
def test_playlist_batching_append_large(mock_get_conn):
    """
    Verifies batching logic in APPEND mode.
    Scenario: Appending 25 tracks to existing playlist.
    Expected:
    - 3 calls to updatePlaylist (10, 10, 5)
    """
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn
    
    # Mock that playlist exists
    mock_conn.getPlaylists.return_value = {
        'playlists': {'playlist': [{'id': 'pl-123', 'name': 'ExistingList'}]}
    }
    
    track_ids = [f"id-{i}" for i in range(25)]
    
    result = manage_playlist(name="ExistingList", operation="append", track_ids=track_ids)
    
    assert "Appended 25 tracks" in result
    
    # createPlaylist should NOT be called
    mock_conn.createPlaylist.assert_not_called()
    
    # updatePlaylist called 3 times
    assert mock_conn.updatePlaylist.call_count == 3
    
    calls = mock_conn.updatePlaylist.call_args_list
    # Call 1: 10 tracks
    assert len(calls[0].kwargs['songIdsToAdd']) == 10
    # Call 2: 10 tracks
    assert len(calls[1].kwargs['songIdsToAdd']) == 10
    # Call 3: 5 tracks
    assert len(calls[2].kwargs['songIdsToAdd']) == 5
    
    assert calls[2].kwargs['songIdsToAdd'] == track_ids[20:25]
