# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

import sys
from unittest.mock import MagicMock
import json
import os

# --- MOCK DEPENDENCIES ---
mcp_mock = MagicMock()
fastmcp_mock = MagicMock()
mcp_mock.server.fastmcp.FastMCP = MagicMock(return_value=fastmcp_mock)
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

# Import server (now in specific folder)
from navidrome_mcp_server import get_smart_candidates

# Setup Mock Connection behavior
mock_conn = MagicMock()
libsonic_mock.Connection.return_value = mock_conn
mock_conn.getAlbumList2.return_value = {
    'albumList2': {
        'album': [
            {'id': '1', 'title': 'Simulated Album', 'artist': 'Test Artist'}
        ]
    }
}

print("--- Executing Tool: get_smart_candidates(mode='recently_added') ---")
# Call the tool
try:
    result = get_smart_candidates(mode="recently_added", limit=5)
    print(f"Tool Result: {result}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Reading Log File: logs/navidrome_mcp.log ---")
if os.path.exists("logs/navidrome_mcp.log"):
    with open("logs/navidrome_mcp.log", "r") as f:
        # Read the last line to show the most recent entry
        lines = f.readlines()
        if lines:
            last_line = lines[-1]
            try:
                data = json.loads(last_line)
                print(json.dumps(data, indent=2))
            except:
                print(last_line)
        else:
            print("Log file is empty.")
else:
    print("Log file not found.")
