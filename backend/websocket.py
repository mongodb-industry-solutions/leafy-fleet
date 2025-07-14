import asyncio  
import websockets  
import logging  
  
logging.basicConfig(level=logging.INFO)  
  
# Define the WebSocket server  
async def handle_request(websocket, path, chain):  
    try:  
        # Simulate generating Chain-of-Thought reasoning in real-time  
        reasoning_steps = chain.split("\n")  
          
        # Stream steps over the WebSocket connection  
        for step in reasoning_steps:  
            logging.info(f"Sending reasoning step: {step.strip()}")  
            await websocket.send(step.strip())  # Send each step to the client  
            await asyncio.sleep(0.5)  # Simulate a delay for each reasoning step  
          
        await websocket.send("[FINAL] Chain-of-Thought reasoning completed.")  # Indicate completion  
          
    except Exception as e:  
        logging.error(f"Error during WebSocket handling: {e}")  
        await websocket.send("[ERROR] Unable to generate reasoning.")  
        await websocket.close()  
  
# Start the WebSocket server  
async def start_websocket_server():  
    server = await websockets.serve(handle_request, "localhost", 8000)  
    logging.info("WebSocket Server Started on ws://localhost:8000")  
    await server.wait_closed()  
  
# Run the WebSocket server  
if __name__ == "__main__":  
    asyncio.run(start_websocket_server())  
