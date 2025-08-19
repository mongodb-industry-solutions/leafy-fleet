import { createSlice } from "@reduxjs/toolkit";

const GeofencesSlice = createSlice({
  name: "Geofences",
  initialState: {

    geofences: [],
  },
    reducers: {
    setGeofences: (state, action) => {
      state.geofences = action.payload.geofences || [];
    },
    addGeofence: (state, action) => {
      const newGeofence = action.payload.geofence;
      if (!state.geofences.some(g => g.name === newGeofence.name)) {
        state.geofences.push(newGeofence);
      }
    },
    removeGeofence: (state, action) => {
      const geofenceName = action.payload.name;
      state.geofences = state.geofences.filter(g => g.name !== geofenceName);
    }
  }
});
export const { setGeofences, addGeofence, removeGeofence } = GeofencesSlice.actions;
export default GeofencesSlice.reducer;