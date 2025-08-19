import { createSlice } from "@reduxjs/toolkit";

const ResultSlice = createSlice({
    name: "Result",
    initialState: {
        results: null,
        staticSelectedCar: null,
        selectedCar: null,
        isModalOpen: false,
    },
    reducers: {
        setResults: (state, action) => {
            state.results = action.payload?.results !== undefined   
                ? action.payload.results   
                : action.payload;  
        },
        setSelectedCar: (state, action) => {
            state.selectedCar = action.payload.car;
            console.log("Selected car in ResultSlice:", state.selectedCar);
        },
        setIsModalOpen: (state, action) => {
            state.isModalOpen = action.payload.isModalOpen;
        },
        setStaticSelectedCar: (state, action) => {  
            state.staticSelectedCar = action.payload.staticCar;  
            console.log("Static selected car in ResultSlice:", state.staticSelectedCar);  
        }  
    }
});

export const { setResults, setSelectedCar, setIsModalOpen,setStaticSelectedCar } = ResultSlice.actions;
export default ResultSlice.reducer;
