import { createSlice } from "@reduxjs/toolkit";
import { act } from "react";

const MessageSlice = createSlice({
    name: "MessageStatus",
    initialState: {
<<<<<<< HEAD
        lastMessageId: 0,

        messageHistory: [{
            id: 0,
            text: 'Hello! I am your AI assistant. How can I help you today?',
            sender: 'bot',
            completed: false,
        }],
        selectedMessage: 0,
        chatbotIsThinking: false,
        chatbotError: null,

    },
    reducers: {
=======
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
>>>>>>> c50fdae5d49a9fa72e2ee0075cf6a2246efbea07
        pushMessageHistory: (state, action) => {
            state.messageHistory = [...state.messageHistory, { ...action.payload.message }]
            state.chatbotIsThinking = false;
            state.chatbotError = null
<<<<<<< HEAD
            state.lastMessageId = action.payload.message.id;
        },
        setSelectedMessage: (state, action) => {
            state.selectedMessage = action.payload.message;
        },
        setIsChatbotThinking: (state, action) => {
            state.chatbotIsThinking = action.payload;
        },
        setAnimationMessage: (state, action) => {
            state.messageHistory = state.messageHistory.map((msg) =>
                msg.id === action.payload.id ? { ...msg, completed: action.payload.completed } : msg
            );
        }


=======
        },
        setSelectedMessage: (state, action) => {
            state.selectedMessage = { ...action.payload.message }

        },
>>>>>>> c50fdae5d49a9fa72e2ee0075cf6a2246efbea07
    },

})

<<<<<<< HEAD
export const { pushMessageHistory, setSelectedMessage, setIsChatbotThinking, setAnimationMessage } = MessageSlice.actions
=======
export const { setState, pushMessageHistory, setSelectedMessage } = MessageSlice.actions
>>>>>>> c50fdae5d49a9fa72e2ee0075cf6a2246efbea07
export default MessageSlice.reducer