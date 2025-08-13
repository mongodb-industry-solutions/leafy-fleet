const API_BASE_URL = 'http://localhost:9001';  
  
export const geospatialAPI = {  
  // Search vehicles nearest to geofence  
  searchNearestVehicles: async (searchParams) => {  
    try {  
      console.log('Sending request:', {
        session_id: searchParams.sessionId,
        geofence_names: searchParams.geoFences,
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
        }),  
      });  
  
      if (!response.ok) {  
        throw new Error(`HTTP error! status: ${response.status}`);  
      }  
  
      const data = await response.json();  
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