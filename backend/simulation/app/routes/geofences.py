from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  

from database import geofences_coll  # Make sure this is your geofences collection

router = APIRouter()

@router.get("/geofences/check")
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