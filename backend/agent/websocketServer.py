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
        self.active_connections: List[tuple[WebSocket, str]] = []

    async def connect(self, websocket: WebSocket, thread_id: str = None):
        """
        Accepts a new WebSocket connection and adds it to the list of active connections.
        """
        await websocket.accept()
        self.active_connections.append((websocket, thread_id))
        logger.info(f"New connection with thread_id: {thread_id}. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the list of active connections.
        """
        self.active_connections = [(ws, tid) for ws, tid in self.active_connections if ws != websocket]
        # logger.info(f"Connection closed. Total clients: {len(self.active_connections)}")

    async def send_to_thread(self, message: str, thread_id: str):
        """
        Sends a message to all connections with a specific thread_id.
        """
        logger.info(f"Sending message to thread_id: {thread_id}")
        connections_to_remove = []
        
        for websocket, tid in self.active_connections[:]:
            if tid == thread_id:
                try:
                    await websocket.send_text(message)
                    logger.info(f"Message sent to thread_id: {thread_id}")
                except (WebSocketDisconnect, RuntimeError):
                    logger.warning(f"Failed to send message to thread_id: {thread_id}, removing connection")
                    connections_to_remove.append(websocket)
        
        # Remove failed connections
        for websocket in connections_to_remove:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all active WebSocket connections.
        
        It iterates over a copy of the list to allow for safe removal of disconnected clients
        if a send operation fails.
        """
        logger.info(f"Broadcasting message to {len(self.active_connections)} client(s)")
        connections_to_remove = []
        
        for websocket, thread_id in self.active_connections[:]:
            try:
                await websocket.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                logger.warning(f"Failed to broadcast to thread_id: {thread_id}, removing connection")
                connections_to_remove.append(websocket)
        
        # Remove failed connections
        for websocket in connections_to_remove:
            self.disconnect(websocket)

# Create a single, global instance of the ConnectionManager
manager = ConnectionManager()