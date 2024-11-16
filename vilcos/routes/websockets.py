# vilcos/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, channel: str = "default"):
        """
        Connect a WebSocket client to a specific channel.
        
        Args:
            websocket: The WebSocket connection
            channel: Channel name for grouping connections (default: "default")
        """
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"Client connected to channel: {channel}")
        
    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        """Remove a WebSocket connection from a channel."""
        if channel in self.active_connections:
            self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info(f"Client disconnected from channel: {channel}")
    
    async def broadcast(self, message: Any, channel: str = "default"):
        """
        Broadcast a message to all connections in a channel.
        
        Args:
            message: The message to broadcast (will be JSON serialized)
            channel: Target channel (default: "default")
        """
        if channel not in self.active_connections:
            return
            
        message_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": message
        }
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message_data)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                await self.disconnect(connection, channel)

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """Send a message to a specific client."""
        message_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": message
        }
        await websocket.send_json(message_data)

manager = ConnectionManager()

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "default"):
    """WebSocket endpoint that handles connections and messages."""
    logger.debug(f"WebSocket connection attempt to channel: {channel}")
    try:
        await manager.connect(websocket, channel)
        logger.debug(f"WebSocket connected successfully to channel: {channel}")
        
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            try:
                # Try to parse as JSON
                message = json.loads(data)
                # Echo the message back to the same channel
                await manager.broadcast(message, channel)
            except json.JSONDecodeError:
                # If not JSON, broadcast as plain text
                await manager.broadcast({"message": data}, channel)
    except WebSocketDisconnect:
        logger.debug(f"WebSocket disconnected from channel: {channel}")
        manager.disconnect(websocket, channel)
    except Exception as e:
        logger.error(f"WebSocket error in channel {channel}: {str(e)}")
        manager.disconnect(websocket, channel)

# Example of how to broadcast from other parts of your application
@router.post("/broadcast/{channel}")
async def broadcast_to_channel(channel: str, message: Dict[str, Any]):
    """
    HTTP endpoint to broadcast a message to a specific channel.
    
    Args:
        channel: Target channel name
        message: Message to broadcast
    """
    await manager.broadcast(message, channel)
    return {"status": "Message broadcast"}

