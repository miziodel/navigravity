# Copyright (c) 2026 Maurizio Delmonte
# SPDX-License-Identifier: MIT

import pytest
import os
import sys
from unittest.mock import MagicMock

# Ensure src is in path so we can import the server
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set environment variables required for the server to import."""
    monkeypatch.setenv("NAVIDROME_URL", "http://mock.url")
    monkeypatch.setenv("NAVIDROME_USER", "mock_user")
    monkeypatch.setenv("NAVIDROME_PASS", "mock_pass")

@pytest.fixture
def mock_conn(mocker):
    """Mock the libsonic connection used in the server."""
    # We need to patch navidrome_mcp_server.libsonic.Connection BEFORE it is used in get_conn
    # But since we import get_conn, we should ideally patch where it's used or return a mock
    # that get_conn will return.
    
    # Actually, the server creates a new Connection instance in get_conn()
    # so we should patch libsonic.Connection
    mock_connection_class = mocker.patch("navidrome_mcp_server.libsonic.Connection")
    mock_instance = mock_connection_class.return_value
    return mock_instance
