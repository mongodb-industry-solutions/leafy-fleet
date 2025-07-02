import { USER_MAP } from "@/lib/constants";
import { createSlice } from "@reduxjs/toolkit";

const UserSlice= createSlice({
    name: "User",
    initialState: {
        list: USER_MAP || [],
        selectedUser: USER_MAP[0],
       
    },
    reducers: {
        setSelectedUser: (state, action) => {
            state.selectedUser = action.payload.user
            
        }
    },       
})

export const { 
    setSelectedUser 
} = UserSlice.actions

export default UserSlice.reducer