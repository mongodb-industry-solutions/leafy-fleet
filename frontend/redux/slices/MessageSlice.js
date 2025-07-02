import { createSlice } from "@reduxjs/toolkit";
import { act } from "react";

const MessageSlice = createSlice({
    name: "MessageStatus",
    initialState: {
        messageId: null,
        isSelected: false,

        messageHistory: [{
            id: 'initial',
            text: 'Hello! I am your AI assistant. How can I help you today?',
            sender: 'bot'
        }],
        selectedMessage: null,
        chatbotIsThinking: false,
        chatbotError: null

    },
    reducers: {
        setState: (state, action) => {
            state.messageId = action.payload.messageId;
            state.isSelected = true;
        },
        pushMessageHistory: (state, action) => {
            state.messageHistory = [...state.messageHistory, { ...action.payload.message }]
            state.chatbotIsThinking = false;
            state.chatbotError = null
        },
        setSelectedMessage: (state, action) => {
            state.selectedMessage = { ...action.payload.message }

        },
    },

})

export const { setState, pushMessageHistory, setSelectedMessage } = MessageSlice.actions
export default MessageSlice.reducer