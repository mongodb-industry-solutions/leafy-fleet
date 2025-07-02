import { configureStore } from "@reduxjs/toolkit";
import UserReducer from './slices/UserSlice.js'

const store = configureStore({
    reducer: {
        User: UserReducer,
     
        // Catalog
        // Chatbot
        // Authentication
        // COnfiguration
    },
})

export default store