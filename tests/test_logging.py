# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

import sys
from unittest.mock import MagicMock

# --- MOCK DEPENDENCIES BEFORE IMPORT ---
# We mock mcp and libsonic because they might not be installed in the test env
mcp_mock = MagicMock()
fastmcp_mock = MagicMock()
mcp_mock.server.fastmcp.FastMCP = MagicMock(return_value=fastmcp_mock)
# Ensure the decorator works as a simple pass-through or capture
def tool_decorator(name=None, description=None):
    def decorator(func):
        return func
    return decorator
fastmcp_mock.tool = MagicMock(side_effect=tool_decorator)

sys.modules["mcp"] = mcp_mock
sys.modules["mcp.server"] = mcp_mock.server
sys.modules["mcp.server.fastmcp"] = mcp_mock.server.fastmcp

libsonic_mock = MagicMock()
sys.modules["libsonic"] = libsonic_mock

# Now we can import
import pytest
import logging
import json
import os
from navidrome_mcp_server import get_smart_candidates, assess_playlist_quality

def test_logging_execution_metadata(mock_conn, caplog):
    """Verify that tool execution logs metadata correctly."""
    # Setup mock return for get_smart_candidates
    mock_conn.getAlbumList2.return_value = {
        'albumList2': {
            'album': []
        }
    }
    
    # We need to capture logs from our specific logger
    logger = logging.getLogger("navidrome_mcp")
    logger.setLevel(logging.INFO)
    
    # Execute tool
    with caplog.at_level(logging.INFO, logger="navidrome_mcp"):
        res = get_smart_candidates(mode="recently_added", limit=5)
        
    # Analyze logs
    assert len(caplog.records) > 0
    record = caplog.records[0]
    
    assert hasattr(record, "tool")
    assert record.tool == "get_smart_candidates"
    assert hasattr(record, "inputs")
    assert record.inputs['kwargs']['mode'] == "recently_added"
    assert hasattr(record, "result_summary")
    assert record.result_summary['count'] == 0 

def test_logging_quality_assessment(mock_conn, caplog):
    """Verify that quality assessment logs score."""
    # Mock getSong
    mock_conn.getSong.side_effect = lambda id: {'song': {'id': id, 'artist': 'Artist A'}}
    
    with caplog.at_level(logging.INFO, logger="navidrome_mcp"):
        assess_playlist_quality(["1", "2"])
        
    record = caplog.records[0]
    assert record.tool == "assess_playlist_quality"
    assert "diversity_score" in record.result_summary
    assert record.result_summary["diversity_score"] == 0.5

def test_log_file_creation(mock_conn):
    """Verify that the log file is actually created and contains valid JSON."""
    log_file = "logs/navidrome_mcp.log"
    
    try:
        # Run a command
        get_smart_candidates(mode="recently_added", limit=1)
        
        # Check file
        assert os.path.exists(log_file)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
            # Find the line corresponding to this run (it might be appended)
            # We explicitly look for the entry with tool="get_smart_candidates"
            found = False
            for line in reversed(lines):
                 try:
                    data = json.loads(line)
                    if data.get("tool") == "get_smart_candidates":
                        found = True
                        break
                 except: continue
                 
            assert found, "Could not find log entry in file"
    finally:
        pass
