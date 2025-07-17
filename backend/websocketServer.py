# connection_manager.py

from typing import List
import logging
from fastapi import WebSocket, WebSocketDisconnect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections and message broadcasting."""
    def __init__(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the list of active connections.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New connection: {websocket.client}. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the list of active connections.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Connection closed: {websocket.client}. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all active WebSocket connections.
        
        It iterates over a copy of the list to allow for safe removal of disconnected clients
        if a send operation fails.
        """
        logger.info(f"Broadcasting message: '{message}' to {len(self.active_connections)} client(s)")
        # Iterate over a copy of the list to avoid issues with modifying it during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                # The RuntimeError can happen if the connection is closing.
                # If a client disconnects without a proper closing handshake,
                # we'll catch it here and remove them.
                self.disconnect(connection)

# Create a single, global instance of the ConnectionManager
manager = ConnectionManager()