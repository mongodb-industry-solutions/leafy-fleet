import { USER_MAP } from "@/lib/constants";
import { createSlice } from "@reduxjs/toolkit";

const UserSlice = createSlice({
  name: "User",
  initialState: {
    list: USER_MAP || [],
    selectedUser: USER_MAP[0],
    selectedFleets: 1,
    fleet1Name: "Fleet 1",
    fleet2Name: "Fleet 2",
    fleet3Name: "Fleet 3",
    fleet1Capacity: null,
    fleet2Capacity: null,
    fleet3Capacity: null,
    fleet1Attributes: ["Latitude","Performance","Run Time","Longitude","Avaliability","Quality"],
    fleet2Attributes: ["Latitude","Performance","Run Time","Longitude","Avaliability","Quality",],
    fleet3Attributes: ["Latitude","Performance","Run Time","Longitude","Avaliability","Quality",],
    editFleet: 1,
    isLoggedIn: false,
    sessionId: 'gio2' ,
  },
  reducers: {
    setSelectedUser: (state, action) => {
      state.selectedUser = { ...action.payload.user };
    },
    setFleet1Capacity: (state, action) => {
      state.fleet1Capacity = action.payload;
    },
    setFleet2Capacity: (state, action) => {
      state.fleet2Capacity = action.payload;
    },
    setFleet3Capacity: (state, action) => {
      state.fleet3Capacity = action.payload;
    },
    setFleet1Name: (state, action) => {
      state.fleet1Name = action.payload;
    },
    setFleet2Name: (state, action) => {
      state.fleet2Name = action.payload;
    },
    setFleet3Name: (state, action) => {
      state.fleet3Name = action.payload;
    },
    setSelectedFleets: (state,action) =>{
      state.selectedFleets = action.payload.selectedFleets;
    },
    setFleet1Attributes: (state, action) => {
      state.fleet1Attributes = action.payload;
    },
    setFleet2Attributes: (state, action) => {
      state.fleet2Attributes = action.payload;
    },
    setFleet3Attributes: (state, action) => {
      state.fleet3Attributes = action.payload;
    },
    setEditFleet:(state, action) => {
      state.editFleet = action.payload.editFleet;
    },
    setLoggedFleet: (state, action) => {
      state.isLoggedIn = action.payload; // Set the login status based on the action payload
    },
    setSessionId: (state, action) => {  
      state.sessionId = action.payload.sessionId;  
    }  


}

});

export const {
  setSelectedUser,
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
  setFleet1Name,
  setFleet2Name,
  setFleet3Name,
  setSelectedFleets,
  setFleet1Attributes,
  setFleet2Attributes,
  setFleet3Attributes,
  setEditFleet,
  setLoggedFleet,
  setSessionId    
} = UserSlice.actions;

export default UserSlice.reducer;
