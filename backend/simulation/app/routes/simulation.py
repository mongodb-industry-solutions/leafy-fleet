import asyncio  
from fastapi import APIRouter, HTTPException, BackgroundTasks  
from car_manager import create_cars, get_all_cars, clear_all_cars  
from car_history_manager import clear_h_all_cars
from state_manager import is_running, is_stopped, is_paused, set_state  
from global_context import get_session, timeseries_get , latest_telemetry # Import HTTP_SESSION management functions  
import logging  


logger = logging.getLogger(__name__)  
router = APIRouter()  
  
# Global simulation tasks list  
SIMULATION_TASKS = []  
HISTORY_TASKS = []
ACTIVE_USERS = 0  

def increment_active_users():  
    """Increment the active user counter."""  
    global ACTIVE_USERS  
    ACTIVE_USERS += 1  
    logger.info(f"Active users incremented to: {ACTIVE_USERS}")  
    return ACTIVE_USERS  
  
def decrement_active_users():  
    """Decrement the active user counter."""  
    global ACTIVE_USERS  
    ACTIVE_USERS = max(0, ACTIVE_USERS - 1)  # Prevent negative counts  
    logger.info(f"Active users decremented to: {ACTIVE_USERS}") 
    if get_active_users() == 0:
        # If no active users, stop the simulation
        set_state("stopped")
        logger.info("No active users left, stopping simulation")
        asyncio.create_task(stop_simulation_internal()) 
    return ACTIVE_USERS  
  
def get_active_users():  
    """Get the current active user count."""  
    return ACTIVE_USERS  
  
async def stop_simulation():  
    """Stop the simulation and clean up all resources."""  
    if is_stopped():  
        raise HTTPException(status_code=400, detail="Simulation is already stopped")  
  
    await stop_simulation_internal()  
    logger.info("Simulation stopped and cleaned up")  
  
  

async def stop_simulation_internal():  
    """Internal function to stop simulation and clean up tasks."""  
    global SIMULATION_TASKS  
    global HISTORY_TASKS

    # Update simulation state first
    set_state("stopped")  
    
    # Cancel all running tasks first
    all_tasks = SIMULATION_TASKS + HISTORY_TASKS
    for task in all_tasks:  
        if not task.done():  
            task.cancel()  
    
    # Wait for tasks to complete with proper timeout
    if all_tasks:  
        try:  
            await asyncio.wait_for(  
                asyncio.gather(*all_tasks, return_exceptions=True),  
                timeout=10.0,  # Reduced timeout since we cancelled them
            )  
            logger.info("All simulation and history tasks stopped successfully")
        except asyncio.TimeoutError:  
            logger.warning("Some tasks did not complete within timeout")  
        except Exception as e:
            logger.warning(f"Exception during task cleanup: {e}")
  
    # Clear task lists
    SIMULATION_TASKS.clear()  
    HISTORY_TASKS.clear()
    
    # Clear cars after tasks are done
    await clear_h_all_cars()
    await clear_all_cars()
    
    logger.info("Simulation cleanup completed")
  
async def pause_simulation():  
    """Pause the simulation."""  
    if not is_running():  
        raise HTTPException(status_code=400, detail="Simulation is not running")  
  
    set_state("paused")  
    logger.info("Simulation paused")  
  
  
async def resume_simulation():  
    """Resume the paused simulation."""  
    if not is_paused():  
        raise HTTPException(status_code=400, detail="Simulation is not paused")  
  
    set_state("running")  
    logger.info("Simulation resumed")  

@router.post("/reduce-users")
async def reduce_users():
    """Endpoint to decrement active users."""
    decrement_active_users()
    return {"active_users": get_active_users()}
  
@router.post("/start/{num_cars}")  
async def start_simulation_endpoint(num_cars: int):  
    """  
    Start the simulation with a given number of cars.  
    Args:  
        num_cars (int): Number of cars to create.  
    """  
    if num_cars <= 0:  
        raise HTTPException(status_code=400, detail="Number of cars must be greater than 0")  
  
    if is_running() or is_paused():  
        raise HTTPException(status_code=400, detail="Simulation is already running")  
    

    # Stop any active simulation to ensure a clean slate  
    await stop_simulation_internal()  
  
    global SIMULATION_TASKS  
    session = get_session()  # Safely retrieve HTTP_SESSION  
    cars = await create_cars(num_cars)  # Pass session explicitly to car creation  
  
    logger.info(f"HTTP_SESSION: {session}")  # Confirm HTTP_SESSION existence  
  
    # Spawn asynchronous tasks for each car  
    SIMULATION_TASKS = [asyncio.create_task(car.run(session)) for car in cars]  
    logger.info(f"Spawned {len(SIMULATION_TASKS)} simulation tasks.")  
  
    set_state("paused")      
    return {"message": f"Started simulation with {len(cars)} cars."}  
  
  
@router.post("/stop")  
async def stop_simulation_endpoint(background_tasks: BackgroundTasks):  
    """Stop the simulation."""  
    if is_stopped():  
        raise HTTPException(status_code=400, detail="Simulation is already stopped")  
  
    background_tasks.add_task(stop_simulation_internal)  # Offload cleanup to background task  
    return {"message": "Simulation stopping..."}  
  
  
@router.post("/pause")  
async def pause_simulation_endpoint():  
    """Pause the simulation."""  
    if not is_running():  
        raise HTTPException(status_code=400, detail="Simulation is not running")  
  
    await pause_simulation()   
    return {"message": "Simulation paused"}  
  
  
@router.post("/resume")  
async def resume_simulation_endpoint():  
    """Resume the simulation."""  
    if not is_paused():  
        raise HTTPException(status_code=400, detail="Simulation is not paused")  
  
    await resume_simulation()  
    return {"message": "Simulation resumed"}  
  
  
@router.get("/")  
async def health_check():  
    """Health check endpoint."""  
    return {"message": "Car Simulation Microservice is running"}  
