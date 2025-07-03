import { USER_MAP } from "@/lib/constants";
import { createSlice } from "@reduxjs/toolkit";

const UserSlice= createSlice({
    name: "User",
    initialState: {
        list: USER_MAP || [],
        selectedUser: USER_MAP[0],
        selectedFleets: 0,
        fleet1Capacity: 0,
        fleet2Capacity: 0,
        fleet3Capacity: 0,
       
    },
    reducers: {
        setSelectedUser: (state, action) => {
            state.selectedUser = {...action.payload.user}
            
        },
        setFleet1Capacity: (state, action) => {
            state.fleet1Capacity = action.payload.capacity;
        },
        setFleet2Capacity: (state, action) => {
            state.fleet2Capacity = action.payload.capacity;
        },
        setFleet3Capacity: (state, action) => {
            state.fleet3Capacity = action.payload.capacity;
        },
    },
})

export const { 
    setSelectedUser,
    setFleet1Capacity,
    setFleet2Capacity,
    setFleet3Capacity
} = UserSlice.actions

export default UserSlice.reducer