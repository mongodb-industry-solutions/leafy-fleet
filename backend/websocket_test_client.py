"""
Example WebSocket client to test real-time agent workflow updates.
"""

import asyncio
import websockets
import json
from datetime import datetime


async def websocket_client():
    """
    Connect to the WebSocket server and listen for agent workflow updates.
    """
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to WebSocket server at {uri}")
            print("🔄 Listening for agent workflow updates...\n")
            
            while True:
                try:
                    # Receive message from server
                    message = await websocket.recv()
                    
                    # Try to parse as JSON for structured messages
                    try:
                        data = json.loads(message)
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        if data.get("type") == "workflow_start":
                            print(f"[{timestamp}] 🚀 WORKFLOW STARTED")
                            print(f"             Thread ID: {data.get('thread_id')}")
                            print(f"             Query: {data.get('query')}")
                            print()
                            
                        elif data.get("type") == "workflow_progress":
                            step = data.get("step", 0)
                            total = data.get("total_steps", 0)
                            node_id = data.get("node_id", "")
                            status = data.get("status", "")
                            progress = data.get("progress_percentage", 0)
                            
                            status_emoji = {
                                "starting": "🔄",
                                "completed": "✅",
                                "error": "❌"
                            }.get(status, "ℹ️")
                            
                            print(f"[{timestamp}] {status_emoji} Step {step}/{total} ({progress}%) - {node_id}")
                            if data.get("message"):
                                print(f"             {data.get('message')}")
                            print()
                            
                        elif data.get("type") == "tool_status":
                            tool_name = data.get("tool_name", "")
                            status = data.get("status", "")
                            message = data.get("message", "")
                            
                            status_emoji = {
                                "starting": "🔄",
                                "processing": "⚙️",
                                "completed": "✅",
                                "error": "❌"
                            }.get(status, "ℹ️")
                            
                            print(f"[{timestamp}]     {status_emoji} {tool_name}: {message}")
                            
                            # Show additional data if present
                            for key, value in data.items():
                                if key not in ["type", "tool_name", "status", "message", "timestamp"]:
                                    print(f"               {key}: {value}")
                            print()
                            
                        elif data.get("type") == "workflow_complete":
                            print(f"[{timestamp}] 🎉 WORKFLOW COMPLETED")
                            print(f"             Thread ID: {data.get('thread_id')}")
                            recommendation = data.get('recommendation', '')
                            if recommendation:
                                print(f"             Recommendation: {recommendation[:100]}...")
                            print()
                            
                        elif data.get("type") == "workflow_error":
                            print(f"[{timestamp}] ❌ WORKFLOW ERROR")
                            print(f"             Thread ID: {data.get('thread_id')}")
                            print(f"             Error: {data.get('error')}")
                            print()
                            
                        else:
                            # Unknown structured message
                            print(f"[{timestamp}] 📋 {data}")
                            print()
                            
                    except json.JSONDecodeError:
                        # Plain text message
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] 💬 {message}")
                        print()
                        
                except websockets.exceptions.ConnectionClosed:
                    print("❌ WebSocket connection closed")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
    except ConnectionRefusedError:
        print(f"❌ Could not connect to WebSocket server at {uri}")
        print("   Make sure the FastAPI server is running")
    except Exception as e:
        print(f"❌ WebSocket client error: {e}")


def main():
    """
    Main function to run the WebSocket client.
    """
    print("🔌 Starting WebSocket Client")
    print("   Connect to: ws://localhost:8000/ws")
    print("   Press Ctrl+C to exit\n")
    
    try:
        asyncio.run(websocket_client())
    except KeyboardInterrupt:
        print("\n👋 WebSocket client stopped")


if __name__ == "__main__":
    main()
