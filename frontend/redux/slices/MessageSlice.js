import { createSlice } from "@reduxjs/toolkit";

const MessageSlice = createSlice({
  name: "MessageStatus",
  initialState: {
    lastMessageId: 0,
    messageHistory: [
      {
        id: 0,
        text: "Hello! I am your AI assistant. How can I help you today?",
        sender: "bot",
        completed: true,
        agent_profiles: " ",
        checkpoint: " ",
        created_at: " ",
        recommendation_data: " ",
        reported_query: " ", // This is the user question
        thread_id: " ",
        used_tools: " ",
      },
    ],
    selectedMessage: 0,
    chatbotIsThinking: false,
    thinkingMessageId: null,
    chatbotError: null,
    currentThought: "",
  },
  reducers: {
    pushMessageHistory: (state, action) => {
      state.messageHistory = [
        ...state.messageHistory,
        { ...action.payload.message },
      ];
      state.chatbotError = null;
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
        msg.id === action.payload.id
          ? { ...msg, completed: action.payload.completed }
          : msg
      );
    },
    setLatestThought: (state, action) => {
      state.currentThought = action.payload.thought;
    },
    updateMessageText: (state, action) => {
      console.log("Updating message text:", action.payload);
      console.log("Message history before update:", state.messageHistory);

      // Find the index of the message to update
      const messageIndex = state.messageHistory.findIndex(
        (msg) => msg.id === action.payload.id
      );

      if (messageIndex !== -1) {
        // Create a new message object with updated properties
        const updatedMessage = {
          ...state.messageHistory[messageIndex],
          text: action.payload.text,
          agent_profiles: action.payload.agent_profiles,
          checkpoint: action.payload.checkpoint,
          created_at: action.payload.created_at,
          recommendation_data: action.payload.recommendation_data,
          reported_query: action.payload.reported_query,
          thread_id: action.payload.thread_id,
          used_tools: action.payload.used_tools,
        };

        // Replace the message at the specific index
        state.messageHistory[messageIndex] = updatedMessage;
      }

      console.log("Message history after update:", state.messageHistory);
    },
    setThinkingMessageId: (state, action) => {
      state.thinkingMessageId = action.payload;
    },
  },
});

export const {
  pushMessageHistory,
  setSelectedMessage,
  setIsChatbotThinking,
  setAnimationMessage,
  setLatestThought,
  updateMessageText,
  setThinkingMessageId,
} = MessageSlice.actions;
export default MessageSlice.reducer;
