"use client"

import styles from './ChatComponene.module.css'
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import ChatInput from '@/components/ChatInput/ChatInput';
import { useState, useRef, useEffect } from 'react';
import TextBubbleComponent from '@/components/TextBubbleComponent/TextBubbleComponent';


const initialMessage = {
    id: 'initial',
    text: 'Hello! I am your AI assistant. How can I help you today?',
    sender: 'bot'
};

let nextId = 1;

const ChatComponent = () => {

    const bottomRef = useRef(null);
    const [messages, setMessages] = useState([initialMessage]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);


    const handleSendMessage = async (userMessageText) => {

        const newUserMessage = {
            id: nextId++,
            text: userMessageText,
            sender: 'user',
        };
        setMessages(prev => [...prev, newUserMessage]);
        console.log("User message added:", newUserMessage);
    }

    return (
        <div className={styles.chatComponent}>
            <div className={styles.messagesContainer}>
                {messages.map((msg) => (
                    <div key={msg.id}>
                        <TextBubbleComponent user={msg.sender} text={msg.text} />
                    </div>
                ))}
                <div ref={bottomRef} /> {/* 👈 Scroll target */}
            </div>

            <div className={styles.chatBox}>
                <ChatInput onSendMessage={handleSendMessage} />
            </div>
        </div>
    );
}

module.exports = ChatComponent;