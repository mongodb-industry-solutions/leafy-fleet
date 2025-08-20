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
    const socket = new WebSocket(`ws://${process.env.NEXT_PUBLIC_AGENT_SERVICE_URL}/ws?thread_id=${thread_id}`);
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
        "I’m sorry, I’m experiencing technical difficulties. Please try again later.",
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
      const res = await fetch(
        `http://${process.env.NEXT_PUBLIC_AGENT_SERVICE_URL}/run-agent?query_reported=${encodeURIComponent(
          userMessageText
        )}&thread_id=${thread_id}&filters=${encodeURIComponent(
          JSON.stringify(filters)
        )}&preferences=${encodeURIComponent(JSON.stringify(userPreferences))}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

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
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const text = await res.text();
      // console.log("Response text:", text);
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
