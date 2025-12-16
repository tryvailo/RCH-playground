"""
State Manager
Manages global application state (WebSocket connections, test results, etc.)
"""
from typing import Dict, Any
from fastapi import WebSocket

# Global state
active_connections: Dict[str, WebSocket] = {}
test_results_store: Dict[str, Dict] = {}

