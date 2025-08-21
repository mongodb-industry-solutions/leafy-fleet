import { createSlice } from "@reduxjs/toolkit";  
  
const GeofencesSlice = createSlice({  
  name: "Geofences",  
  initialState: {  
    all_geofences: [],  
  },  
  reducers: {  
    setGeofences: (state, action) => {  
      state.all_geofences = action.payload.geofences || [];  
    },  
    addGeofence: (state, action) => {  
      const newGeofence = action.payload.geofence;  
      if (!state.all_geofences.some(g => g.name === newGeofence.name)) {  
        state.all_geofences.push(newGeofence); // Fixed this line  
      }  
    }, 
  }  
});  
  
export const { setGeofences, addGeofence } = GeofencesSlice.actions;  
export default GeofencesSlice.reducer;  