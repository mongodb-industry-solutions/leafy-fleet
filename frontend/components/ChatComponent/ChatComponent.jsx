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
} from "@/redux/slices/MessageSlice";

const ChatComponent = () => {
  // useRef to hold the WebSocket instance
  const socketRef = useRef(null);

  const [connectionStatus, setConnectionStatus] = useState("Not Connected");

  useEffect(() => {
    // 1. Create a new WebSocket connection when the component mounts
    const socket = new WebSocket("ws://localhost:8000/ws");
    socketRef.current = socket; // Store it in the ref

    socket.onopen = () => {
      console.log("WebSocket connection established");
      setConnectionStatus("Connected");
    };

    // 2. Set up the onmessage event listener
    socketRef.current.onmessage = (event) => {
      const receivedData = event.data;
      try {
        const parsedData = JSON.parse(receivedData);
        console.log("Received WebSocket data:", parsedData);

        // Store or process incoming WebSocket updates
        dispatch(setLatestThought({ thought: parsedData.message }));
      } catch (error) {
        console.error("Error parsing WebSocket data:", error);
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

  async function fetchLLMResponse(userMessageText) {
    const response = await fetch(
      `http://localhost:8000/run-agent?query_reported=${encodeURIComponent(
        userMessageText
      )}`
    );
    const data = await response.json();
    return data;
  }

  async function sendMessageOverWebSocket(message) {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not open. Unable to send message.");
    }
  }

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

    try {
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        const command = {
          type: "run_agent",
          query: userMessageText,
        };
        socketRef.current.send(JSON.stringify(command));
      } else {
        console.error("WebSocket is not open!");
      }

      const res = await fetch(
        `http://localhost:8000/run-agent?query_reported=${encodeURIComponent(
          userMessageText
        )}`
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
      try {
        data = JSON.parse(text); // Parse JSON if valid
      } catch (jsonParseError) {
        console.error("Error parsing JSON:", jsonParseError);
        data = {
          chain_of_thought: "Invalid response format. Please contact support.",
        }; // Fallback
      }

      console.log("Received data:", data);
      dispatch(setIsChatbotThinking(false));
    } catch (error) {
      console.error("Error fetching data:", error);
      dispatch(setIsChatbotThinking(false));
      // Already set default fallback data
    }
    const botResponseMessage = {
      id: lastMessageId + 2,
      text: data.chain_of_thought,
      sender: "bot",
      completed: false,
    };
    dispatch(
      pushMessageHistory({
        message: botResponseMessage,
        id: botResponseMessage.id,
      })
    );
  };
  return (
    <div className={styles.chatComponent}>
      <div className={styles.messagesContainer}>
        {messages.map((msg) => (
          <div key={msg.id}>
            <TextBubbleComponent
              user={msg.sender}
              text={msg.text}
              id={msg.id}
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
