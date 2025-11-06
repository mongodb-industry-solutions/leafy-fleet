"use client";

import styles from "./ChatComponene.module.css";

import ChatInput from "@/components/ChatInput/ChatInput";
import { useRef, useEffect, useState } from "react";
import TextBubbleComponent from "@/components/TextBubbleComponent/TextBubbleComponent";
import { useDispatch, useSelector } from "react-redux";
import {
  pushMessageHistory,
  setIsChatbotThinking,
  setLatestThought,
  updateMessageText,
  setThinkingMessageId,
} from "@/redux/slices/MessageSlice";
import { Body } from "@leafygreen-ui/typography";

const ChatComponent = () => {
  // useRef to hold the WebSocket instance
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState("Not Connected");

  const filters = useSelector((state) => state.User.queryFilters); // At top level of component

  const fleet1Atributes = useSelector((state) => state.User.fleet1Attributes);
  const fleet2Atributes = useSelector((state) => state.User.fleet2Attributes);
  const fleet3Atributes = useSelector((state) => state.User.fleet3Attributes);
  const fleet1Capacity = useSelector((state) => state.User.fleet1Capacity);
  const fleet2Capacity = useSelector((state) => state.User.fleet2Capacity);
  const fleet3Capacity = useSelector((state) => state.User.fleet3Capacity);
  const thread_id = useSelector((state) => state.User.sessionId);

  const userPreferences = [
    [...fleet1Atributes, fleet1Capacity],
    [...fleet2Atributes, fleet2Capacity],
    [...fleet3Atributes, fleet3Capacity],
  ];

  useEffect(() => {
    // 1. Create a new WebSocket connection when the component mounts
    // Use the current host instead of hardcoded 127.0.0.1
    // This allows WebSocket to work both locally and in Kubernetes
    const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = typeof window !== 'undefined' ? window.location.host : 'localhost:3000';
    const wsUrl = `${protocol}//${host}/ws?thread_id=${thread_id}`;

    console.log('[ChatComponent DEBUG] WebSocket URL:', wsUrl);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket; // Store it in the ref

    socket.onopen = () => {
      console.log("WebSocket connection established");
      setConnectionStatus("Connected");
    };

    // 2. Set up the onmessage event listener
    socketRef.current.onmessage = (event) => {
      // console.log("WebSocket message received:", event);
      try {
        dispatch(setLatestThought({ thought: event.data }));
      } catch (error) {
        // console.error("Error parsing WebSocket data:", error);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
      setConnectionStatus("Closed");
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
      setConnectionStatus("Error");
    };

    // 3. Cleanup function: close the connection when the component unmounts
    return () => {
      console.log("Closing WebSocket connection");
      socket.close();
    };
  }, []); // The empty dependency array [] means this effect runs only once on mount

  const bottomRef = useRef(null);
  const lastMessageId = useSelector((state) => state.Message.lastMessageId);
  const dispatch = useDispatch();
  const messages = useSelector((state) => state.Message.messageHistory);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (userMessageText) => {
    const newUserMessage = {
      id: lastMessageId + 1,
      text: userMessageText,
      sender: "user",
      completed: true,
    };
    dispatch(
      pushMessageHistory({ message: newUserMessage, id: newUserMessage.id })
    );

    dispatch(setIsChatbotThinking(true));
    let data = {
      chain_of_thought:
        "Sending question... ",
    }; // Default fallback

    const botResponseMessage = {
      id: lastMessageId + 2,
      text: data.chain_of_thought,
      sender: "bot",
      completed: false,
    };
    dispatch(setThinkingMessageId(lastMessageId + 2));
    dispatch(
      pushMessageHistory({
        message: botResponseMessage,
        id: botResponseMessage.id,
      })
    );

    try {
      // Use Next.js API route instead of direct backend call
      // This allows the request to be made server-side where 127.0.0.1 works
      const url = `/api/run-agent?query_reported=${encodeURIComponent(
        userMessageText
      )}&thread_id=${thread_id}&filters=${encodeURIComponent(
        JSON.stringify(filters)
      )}&preferences=${encodeURIComponent(JSON.stringify(userPreferences))}`;

      console.log('[ChatComponent DEBUG] Calling agent API route:', url);
      console.log('[ChatComponent DEBUG] User preferences:', userPreferences);
      console.log('[ChatComponent DEBUG] Filters:', filters);
      console.log('[ChatComponent DEBUG] Thread ID:', thread_id);

      const res = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      //   const res = {
      //     ok: true,
      //     status: 200,
      //     text: async () =>
      //       JSON.stringify({
      //         chain_of_thought: `This is a simulated response for the query: "${userMessageText}". Replace this with actual LLM response.`,
      //       }),
      //   }

      // Check if the response is OK (status 200)
      if (!res.ok) {
        console.error("[ChatComponent DEBUG] HTTP error! status:", res.status);
        const errorText = await res.text();
        console.error("[ChatComponent DEBUG] Error response:", errorText);
        let data = {
          chain_of_thought:
            "I'm sorry, I'm experiencing technical difficulties. Please try again later.",
        };
        dispatch(setIsChatbotThinking(false));
        dispatch(
          updateMessageText({
            id: botResponseMessage.id,
            text: data.chain_of_thought,
          })
        );
        throw new Error(`HTTP error! status: ${res.status}, response: ${errorText}`);
      }

      const text = await res.text();
      console.log("[ChatComponent DEBUG] Response received, length:", text.length);
      console.log("[ChatComponent DEBUG] Response text:", text.substring(0, 200));
      try {
        // Parse JSON if valid
        const parsedData = JSON.parse(text);
        data = parsedData; // Use the parsed data
      } catch (jsonParseError) {
        console.error("Error parsing JSON:", jsonParseError);
        data = {
          recommendation_text: "Invalid response format.",
        }; // Fallback
      }
      dispatch(setIsChatbotThinking(false));
      dispatch(
        updateMessageText({
          id: botResponseMessage.id,
          text: data.recommendation_text,
          agent_profiles: data.agent_profiles,
          checkpoint: data.checkpoint,
          created_at: data.created_at,
          recommendation_data: data.recommendation_data,
          reported_query: data.query_reported,
          thread_id: data.thread_id,
          used_tools: data.used_tools,
        })
      );
    } catch (error) {
      console.error("Error fetching data:", error);
      let data = {
          chain_of_thought:
            "I’m sorry, I’m experiencing technical difficulties. Please try again later.",
        };
        dispatch(setIsChatbotThinking(false));
        dispatch(
          updateMessageText({
            id: botResponseMessage.id,
            text: data.chain_of_thought,
          })
        );
      dispatch(setIsChatbotThinking(false));
      // Already set default fallback data
    }
  };
  return (
    <div className={styles.chatComponent}>
      <div className={styles.messagesContainer}>
        {messages.map((msg, idx) => (
          <div key={`${msg.id}-${idx}`}>
            <TextBubbleComponent
              user={msg.sender}
              text={msg.text}
              id={msg.id}
              thinkingMessageId={msg.id}
            />
          </div>
        ))}

        <div ref={bottomRef} />
      </div>
      <div className={styles.chatBox}>
        <ChatInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};

module.exports = ChatComponent;
