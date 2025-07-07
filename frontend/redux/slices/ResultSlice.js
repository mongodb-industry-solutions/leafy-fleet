import { createSlice } from "@reduxjs/toolkit";

const ResultSlice = createSlice({
    name: "Result",
    initialState: {
        results: [],
        selectedCar: null,
        isModalOpen: false,
    },
    reducers: {
        setResults: (state, action) => {
            state.results = action.payload.results;
        },
        setSelectedCar: (state, action) => {
            state.selectedCar = action.payload.car;
        },
        setIsModalOpen: (state, action) => {
            state.isModalOpen = action.payload.isModalOpen;
        }
    }
});

export const { setResults, setSelectedCar, setIsModalOpen } = ResultSlice.actions;
export default ResultSlice.reducer;
