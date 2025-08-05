from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import vehicles_coll
from datetime import datetime
from model.staticModel import VehicleModel
from model.staticModel import MaintenanceLog

router = APIRouter()

@router.post("/static")
async def create_timeseries_entry(entry: VehicleModel):
    #print("Creating timeseries entry...")
    #print("Received data:", entry)

    try:  
        result = vehicles_coll.insert_one(entry.dict())  
        #print("Insert result:", result)
        return JSONResponse(  
            status_code=status.HTTP_201_CREATED,  
            content=jsonable_encoder({"message": "Vehicle entry created successfully", "id": str(result.inserted_id)})  
        )
       # return {"message": "Timeseries entry created successfully", "id": str(result.inserted_id)}  
    except Exception as e:  
        #print(f"Error: {e}")  # Log the error for debugging  
        return {"message": "Error creating timeseries entry", "error": str(e)}  
    
@router.get("/static")
async def get_all_static_entries():
    try:
        entries = list(vehicles_coll.find())
        # Convert ObjectId to string for JSON serialization
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(entries)
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"message": "Error retrieving static entries", "error": str(e)})
        )

@router.get("/static/{car_id}")
async def get_static_entry_by_id(car_id: int):
    try:
        entry = vehicles_coll.find_one({"car_id": car_id})
        if entry:
            entry["_id"] = str(entry["_id"])  # Convert ObjectId to string for JSON serialization
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(entry)
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=jsonable_encoder({"message": "Static entry not found"})
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"message": "Error retrieving static entry", "error": str(e)})
        )
    
@router.update("/static/{car_id}")
async def update_static_entry(car_id: int, entry: list[MaintenanceLog]):
    try:
        result = vehicles_coll.update_one(
            {"car_id": car_id},
            {"$push": {"maintenance_log": {"$each": [log.dict() for log in entry]}}}
        )
        if result.modified_count > 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder({"message": "Static entry updated successfully"})
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=jsonable_encoder({"message": "Static entry not found"})
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"message": "Error updating static entry", "error": str(e)})
        )