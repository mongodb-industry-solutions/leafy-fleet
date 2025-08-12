import { createSlice } from "@reduxjs/toolkit";

const OverviewSlice = createSlice({
    name: "Overview",
    initialState: {
        type: 'inside',
        fleetsFilter: [],
        geoFences: [],
        location: null, 
        maxDistance: 10000,
        minDistance: 10,
        isLoading: false,  
        error: null,  
        
    },
    reducers: {
        setSelectedType: (state, action) => {
            state.type = action.payload.type;
        },
        setSelectedFleets: (state, action) => {
            state.fleetsFilter = action.payload.fleets;
        },
        setGeoFences: (state, action) => {
            state.geoFences = action.payload.geoFences;
        },
        setLocation: (state, action) => {
            state.location = action.payload.location;
        }
        ,setMaxDistance: (state, action) => {
            state.maxDistance = action.payload.maxDistance;
        },
        setMinDistance: (state, action) => {
            state.minDistance = action.payload.minDistance;
        },
        setLoading: (state, action) => {  
            state.isLoading = action.payload.isLoading;  
        },  
        setError: (state, action) => {  
            state.error = action.payload.error;  
        },   
        clearError: (state) => {  
            state.error = null;  
        },  
        resetSearchParams: (state) => {  
            state.type = 'inside';  
            state.fleetsFilter = [];  
            state.geoFences = [];  
            state.location = null;  
            state.maxDistance = 10000;  
            state.minDistance = 0;  
            state.error = null;  
        }  
    }
});

export const { setSelectedType, setSelectedFleets, setLocation, setGeoFences, setMaxDistance, setMinDistance ,setLoading,  setError,  clearError,  resetSearchParams} = OverviewSlice.actions;
export default OverviewSlice.reducer;