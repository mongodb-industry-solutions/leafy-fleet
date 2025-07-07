import { USER_MAP } from "@/lib/constants";
import { createSlice } from "@reduxjs/toolkit";

const UserSlice = createSlice({
  name: "User",
  initialState: {
    list: USER_MAP || [],
    selectedUser: USER_MAP[0],
    selectedFleets: 0,
    fleet1Name: "Fleet 1",
    fleet2Name: "Fleet 2",
    fleet3Name: "Fleet 3",
    fleet1Capacity: null,
    fleet2Capacity: null,
    fleet3Capacity: null,
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
  },
});

export const {
  setSelectedUser,
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
  setFleet1Name,
  setFleet2Name,
  setFleet3Name,
} = UserSlice.actions;

export default UserSlice.reducer;
