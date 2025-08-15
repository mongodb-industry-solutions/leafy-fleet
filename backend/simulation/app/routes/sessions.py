from fastapi import APIRouter, HTTPException, BackgroundTasks  
from state_manager import is_running , set_state,is_paused,is_stopped 
import logging
from car_manager import get_car_by_id, get_all_cars
from car_history_manager import get_h_car_by_id, get_h_all_cars, create_hist_cars
from pydantic import BaseModel
from .simulation import HISTORY_TASKS
from global_context import get_session,timeseries_get  # Import HTTP_SESSION management functions 
from datetime import datetime , timedelta, timezone
import asyncio
from .simulation import increment_active_users

# Pydantic models for API
class SessionRequest(BaseModel):
    session_id: str
    range1: int  # 0-100: cars 1 to range1
    range2: int  # 0-100: cars 101 to 101+range2-1  
    range3: int  # 0-100: cars 201 to 201+range3-1


logger = logging.getLogger(__name__)  
router = APIRouter()  

@router.post("/sessions")
async def add_sessions(request: SessionRequest):
    """Add session to cars based on three ranges: 1-x1, 101-x2, 201-x3."""
    if is_stopped():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    # Validate ranges
    if not all(0 <= x <= 100 for x in [request.range1, request.range2, request.range3]):
        raise HTTPException(status_code=400, detail="All ranges must be between 0 and 100")
    
    # Generate car ID lists based on ranges
    car_ids = []
    
    # Range 1: cars 1 to range1 (if range1 > 0)
    if request.range1 > 0:
        car_ids.extend(list(range(1, request.range1 + 1)))
    
    # Range 2: cars 101 to 101+range2-1 (if range2 > 0)  
    if request.range2 > 0:
        car_ids.extend(list(range(101, 101 + request.range2)))
    
    # Range 3: cars 201 to 201+range3-1 (if range3 > 0)
    if request.range3 > 0:
        car_ids.extend(list(range(201, 201 + request.range3)))
    
    if not car_ids:
        return {
            "message": "No cars selected (all ranges are 0)",
            "session_id": request.session_id,
            "cars_updated": 0,
            "ranges": {
                "range1": f"1-{request.range1}" if request.range1 > 0 else "none",
                "range2": f"101-{100 + request.range2}" if request.range2 > 0 else "none", 
                "range3": f"201-{200 + request.range3}" if request.range3 > 0 else "none"
            }
        }
    # Add sessions to cars
    cars_updated = 0
    cars_not_found = []
    if is_running() or is_paused():
        for car_id in car_ids:
            car = await get_car_by_id(car_id)
            hc = await get_h_car_by_id(car_id)
            if car:
                await car.add_session(request.session_id)
                cars_updated += 1
                if hc:
                    await hc.add_session(request.session_id)
            else:
                cars_not_found.append(car_id)
    
    result = {
        "message": f"Session {request.session_id} added to {cars_updated} cars",
        "session_id": request.session_id,
        "cars_updated": cars_updated,
        "total_cars_requested": len(car_ids),
        "ranges": {
            "range1": f"1-{request.range1}" if request.range1 > 0 else "none",
            "range2": f"101-{100 + request.range2}" if request.range2 > 0 else "none",
            "range3": f"201-{200 + request.range3}" if request.range3 > 0 else "none"
        }
    }
    increment_active_users()
    if is_paused():
        global HISTORY_TASKS        
        session = get_session()
        hc = await create_hist_cars(request.range1, request.range2, request.range3, request.session_id)
        
        if not hc:
            logger.error("No historic cars were created")
            raise HTTPException(status_code=500, detail="Failed to create historic cars")
            # Check latest timestamp, if any      
        timestamp_data = None                   
        try:          
            url = f"{timeseries_get}:9001/timeseries"          
            fetch = await session.get(url)          
            if fetch.status == 200:          
                response_data = await fetch.json()          
                logger.info(f"Retrieved latest timestamp data: {response_data}")          
                timestamp_str = response_data["timestamp"]          
                
                # MongoDB timestamp is already in ISO format with timezone  
                try:  
                    timestamp_data = datetime.fromisoformat(timestamp_str)  
                    # If it's naive, make it UTC-aware  
                    if timestamp_data.tzinfo is None:  
                        timestamp_data = timestamp_data.replace(tzinfo=timezone.utc)  
                except ValueError:  
                    # Fallback parsing if fromisoformat fails  
                    timestamp_data = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")  
                    timestamp_data = timestamp_data.replace(tzinfo=timezone.utc)  
                
            else:          
                logger.error(f"Failed to fetch timestamp data: {fetch.status}")      
                    
            # Log the exact timestamp received from API          
            logger.info(f"Parsed API timestamp (UTC): {timestamp_data}")          
                    
            # Use UTC consistently for one_hour_ago          
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)          
            logger.info(f"One hour ago (UTC): {one_hour_ago}")         
                    
            if timestamp_data:          
                # Check if API timestamp is newer than 1 hour ago          
                if timestamp_data > one_hour_ago:          
                    # API timestamp is less than 1 hour old, use it          
                    latest_timestamp = timestamp_data          
                    logger.info(f"API timestamp is less than 1 hour old: {latest_timestamp}")          
                    logger.info(f"Updated latest telemetry timestamp: {latest_timestamp}")          
                else:          
                    # API timestamp is more than 1 hour old, use 1 hour ago instead          
                    latest_timestamp = one_hour_ago          
                    logger.info(f"API timestamp is more than 1 hour old: {timestamp_data}")          
                    logger.info(f"Using default latest telemetry timestamp (1 hour ago): {latest_timestamp}")          
            else:          
                # No API timestamp available, use 1 hour ago          
                latest_timestamp = one_hour_ago          
                logger.info(f"No timestamp data found, using default (1 hour ago): {latest_timestamp}")          
                    
        except Exception as e:          
            logger.error(f"Error fetching timestamp data: {e}")          
            # Ensure timezone awareness in the fallback case      
            latest_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)      
            logger.error(f"Using default timestamp (1 hour ago) due to error: {latest_timestamp}")   
        HISTORY_TASKS = []
        for car in hc:
            try:
                task = asyncio.create_task(car.run_history(session, latest_timestamp))
                HISTORY_TASKS.append(task)
                logger.info(f"Created task for car {car.car_id}")
            except Exception as e:
                logger.error(f"Failed to create task for car {car.car_id}: {e}")
        
        logger.info(f"Spawned {len(HISTORY_TASKS)} simulation tasks.")
        set_state("running")
    if cars_not_found:
        result["cars_not_found"] = cars_not_found
    return result

@router.delete("/sessions/{car_id}")
async def clear_car_sessions(car_id: int):
    """Clear all sessions from a specific car."""
    if not is_running():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    car = await get_car_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car {car_id} not found")
    
    await car.clear_sessions()
    return {"message": f"Sessions cleared for car {car_id}"}
