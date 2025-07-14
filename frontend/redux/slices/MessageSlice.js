import { createSlice } from "@reduxjs/toolkit";

const MessageSlice = createSlice({
    name: "MessageStatus",
    initialState: {
        lastMessageId: 0,
        messageHistory: [{
            id: 0,
            text: 'Hello! I am your AI assistant. How can I help you today?',
            sender: 'bot',
            completed: true,
        }],
        selectedMessage: 0,
        chatbotIsThinking: false,
        chatbotError: null,
        currentThought: "",

    },
    reducers: {
        pushMessageHistory: (state, action) => {
            state.messageHistory = [...state.messageHistory, { ...action.payload.message }]
            state.chatbotIsThinking = false;
            state.chatbotError = null
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
        },
        setLatestThought: (state, action) => {
            state.currentThought = action.payload.thought;
        }
    },

})

export const { pushMessageHistory, setSelectedMessage, setIsChatbotThinking, setAnimationMessage, setLatestThought } = MessageSlice.actions
export default MessageSlice.reducer