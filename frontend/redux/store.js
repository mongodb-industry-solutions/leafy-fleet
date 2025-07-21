import { configureStore } from "@reduxjs/toolkit";
import UserReducer from './slices/UserSlice.js'
import OverviewReducer from './slices/OverviewSlice.js'
import MessageReducer from './slices/MessageSlice.js'
import ResultReducer from './slices/ResultSlice.js'
const store = configureStore({
    reducer: {
        User: UserReducer,
        Overview: OverviewReducer,
        Message: MessageReducer,
        Result: ResultReducer, 
        // Catalog
        // Chatbot
        // Authentication
        // COnfiguration
    },
})

export default store