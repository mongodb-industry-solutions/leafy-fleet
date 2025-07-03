import { configureStore } from "@reduxjs/toolkit";
import UserReducer from './slices/UserSlice.js'
import OverviewReducer from './slices/OverviewSlice.js'

const store = configureStore({
    reducer: {
        User: UserReducer,
        Overview: OverviewReducer,
        // Catalog
        // Chatbot
        // Authentication
        // COnfiguration
    },
})

export default store