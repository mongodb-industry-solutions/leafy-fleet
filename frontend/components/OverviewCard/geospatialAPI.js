const API_BASE_URL = `http://${process.env.NEXT_PUBLIC_TIMESERIES_GET_SERVICE_URL}`;  
  
export const geospatialAPI = {  
  // Search vehicles nearest to geofence  
  searchNearestVehicles: async (searchParams) => {  
    try {  
      const fleetFilterInts = searchParams.fleetsFilter ? 
        searchParams.fleetsFilter.map(f => parseInt(f, 10)) : [];

      console.log('Sending request:', {
        session_id: searchParams.sessionId,
        geofence_names: searchParams.location,
        min_distance: searchParams.minDistance || 0,
        max_distance: searchParams.maxDistance || 10000,
        fleets_filter: fleetFilterInts
      });
      const response = await fetch(`${API_BASE_URL}/timeseries/nearest-geofence`, {  
        method: 'POST',  
        headers: {  
          'Content-Type': 'application/json',  
        },  
        body: JSON.stringify({  
          session_id: searchParams.sessionId,  
          geofence_names: [searchParams.location],  
          min_distance: searchParams.minDistance || 0,  
          max_distance: searchParams.maxDistance || 10000,  
          car_id_filter: fleetFilterInts
        }),  
      });  
  
      if (!response.ok) {  
        throw new Error(`HTTP error! status: ${response.status}`);  
      }  
  
      const data = await response.json();  
      console.log('Received data:', data);
      return data;  
    } catch (error) {  
      console.error('Error searching nearest vehicles:', error);  
      throw error;  
    }  
  },  
  
  // Search vehicles inside geofence  
  searchInsideVehicles: async (searchParams) => {  
    try {  
      const response = await fetch(`${API_BASE_URL}/timeseries/inside-geofence`, {  
        method: 'POST',  
        headers: {  
          'Content-Type': 'application/json',  
        },  
        body: JSON.stringify({  
          session_id: searchParams.sessionId,  
          geofence_names: searchParams.geoFences,
          car_id_filter: searchParams.fleetsFilter ? 
            searchParams.fleetsFilter.map(f => parseInt(f, 10)) : []  
        }),  
      });  
  
      if (!response.ok) {  
        throw new Error(`HTTP error! status: ${response.status}`);  
      }  
  
      const data = await response.json();  
      return data;  
    } catch (error) {  
      console.error('Error searching vehicles inside geofence:', error);  
      throw error;  
    }  
  },  
};  