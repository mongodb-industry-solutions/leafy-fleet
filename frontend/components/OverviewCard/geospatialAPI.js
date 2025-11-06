export const geospatialAPI = {
  // Search vehicles nearest to geofence
  searchNearestVehicles: async (searchParams) => {
    try {
      const fleetFilterInts = searchParams.fleetsFilter ?
        searchParams.fleetsFilter.map(f => parseInt(f, 10)) : [];

      const requestBody = {
        session_id: searchParams.sessionId,
        geofence_names: [searchParams.location],
        min_distance: searchParams.minDistance || 0,
        max_distance: searchParams.maxDistance || 10000,
        car_id_filter: fleetFilterInts
      };

      console.log('[geospatialAPI] Nearest vehicles request:', requestBody);

      // Use API route instead of direct backend call
      const response = await fetch(`/api/timeseries-nearest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });  
  
      console.log('[geospatialAPI] Nearest vehicles response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[geospatialAPI] Nearest vehicles error:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('[geospatialAPI] Nearest vehicles data received:', {
        count: data.length,
        sample: data[0],
        allCarIds: data.map(v => v.car_id)
      });
      return data;  
    } catch (error) {  
      console.error('Error searching nearest vehicles:', error);  
      throw error;  
    }  
  },  
  
  // Search vehicles inside geofence
  searchInsideVehicles: async (searchParams) => {
    try {
      const requestBody = {
        session_id: searchParams.sessionId,
        geofence_names: searchParams.geoFences,
        car_id_filter: searchParams.fleetsFilter ?
          searchParams.fleetsFilter.map(f => parseInt(f, 10)) : []
      };

      console.log('[geospatialAPI] Inside geofence request:', requestBody);

      // Use API route instead of direct backend call
      const response = await fetch(`/api/timeseries-inside`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });  
  
      console.log('[geospatialAPI] Inside geofence response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[geospatialAPI] Inside geofence error:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('[geospatialAPI] Inside geofence data received:', {
        count: data.length,
        sample: data[0],
        allCarIds: data.map(v => v.car_id)
      });
      return data;
    } catch (error) {
      console.error('[geospatialAPI] Error searching vehicles inside geofence:', error);
      throw error;
    }
  },
};  