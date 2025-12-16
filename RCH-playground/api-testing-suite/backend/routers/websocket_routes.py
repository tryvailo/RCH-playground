"""
WebSocket Routes for real-time communication
"""
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.dependencies import active_connections

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/test-progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time test progress"""
    connection_id = None
    
    # Accept connection with origin check
    origin = websocket.headers.get("origin")
    allowed_origins = ["http://localhost:3000", "http://localhost:5173"]
    
    if origin and origin not in allowed_origins:
        print(f"⚠️ WebSocket rejected: origin {origin} not allowed")
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    
    try:
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        active_connections[connection_id] = websocket
        print(f"✅ WebSocket connected: {connection_id} from {origin}")
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "WebSocket connected"
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    # Handle client messages (e.g., job_id subscription)
                    if message.get("job_id"):
                        print(f"📨 WebSocket received job_id: {message.get('job_id')}")
                        # Client subscribed to specific job
                except json.JSONDecodeError:
                    # Not JSON, ignore
                    pass
            except Exception as e:
                print(f"⚠️ WebSocket receive error: {e}")
                break
    except WebSocketDisconnect:
        print(f"🔌 WebSocket disconnected: {connection_id}")
        if connection_id and connection_id in active_connections:
            del active_connections[connection_id]
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass
        if connection_id and connection_id in active_connections:
            del active_connections[connection_id]
