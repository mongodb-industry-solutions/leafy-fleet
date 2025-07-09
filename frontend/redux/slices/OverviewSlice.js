import { createSlice } from "@reduxjs/toolkit";

const OverviewSlice = createSlice({
    name: "Overview",
    initialState: {
        type: 'inside',
        fleetsFilter: [],
        geoFences: [],
        location: null, 
        maxDistance: 100000,
        minDistance: 10,
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
        ,
        
        setMaxDistance: (state, action) => {
            state.maxDistance = action.payload.maxDistance;
        },
        setMinDistance: (state, action) => {
            state.minDistance = action.payload.minDistance;
        }
    }
});

export const { setSelectedType, setSelectedFleets, setLocation, setGeoFences, setMaxDistance, setMinDistance } = OverviewSlice.actions;
export default OverviewSlice.reducer;