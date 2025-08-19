from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from fastapi import APIRouter, HTTPException, status, Body

from database import geofences_coll  # Make sure this is your geofences collection

router = APIRouter()
  
@router.get("/geofences")  
async def return_all_geofences():  
    """  
    Return all geofences, including their name and geometry, with centroid.  
    """  
    try:  
        # Synchronously query geofences and convert cursor to list  
        geofences_cursor = geofences_coll.find({}, {"_id": 1, "name": 1, "geometry": 1, "centroid":1})   
        geofences = list(geofences_cursor)  # Convert cursor to list  
  
        if not geofences:  
            return JSONResponse(  
                status_code=404,  
                content={"message": "No geofences found in the collection"}  
            )  
  
        # Format the response  
        formatted_geofences = [  
            {  
                "id": str(geofence["_id"]),  # Convert ObjectId to string  
                "name": geofence.get("name", "Unnamed geofence"),  
                "geometry": geofence.get("geometry"),
                "centroid": geofence.get("centroid", None)  # Include centroid if available  
            }  
            for geofence in geofences  
        ]  
  
        return JSONResponse(  
            status_code=200,  
            content={"geofences": formatted_geofences}  
        )  
  
    except Exception as e:  
        # General exception handling  
        raise HTTPException(  
            status_code=500,  
            detail=f"Failed to retrieve geofences. Error: {str(e)}"  
        )  



@router.post("/geofences/check")
async def check_point_in_geofence(body: dict = Body(...)):
    """
    Check if a point is inside any geofence.
    Expects body: { "coordinates": [lon, lat] }
    """
    coords = body.get("coordinates")
    if not coords or len(coords) != 2:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Body must contain 'coordinates': [lon, lat]"}
        )

    # MongoDB $geoIntersects query
    query = {
        "geometry": {
            "$geoIntersects": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coords
                }
            }
        }
    }

    geofence = geofences_coll.find_one(query)
    if geofence:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"geofence_name": geofence.get("name", "Unnamed geofence")}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Not inside any geofence"}
        )