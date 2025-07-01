"use client"

import styles from './ChatComponene.module.css'
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import ChatInput from '@/components/ChatInput/ChatInput';
import { useState, useRef, useEffect } from 'react';

const initialMessage = {
    id: 'initial',
    text: 'Hello! I am your AI assistant. How can I help you today?',
    sender: 'bot'
};

let nextId = 1;

const ChatComponent = () => {

    const [messages, setMessages] = useState([initialMessage]);

    const handleSendMessage = async (userMessageText) => {

        const newUserMessage = {
            id: nextId++,
            text: userMessageText,
            sender: 'user',
        };
        setMessages(prev => [...prev, newUserMessage]);
        console.log("User message added:", newUserMessage);
    }

    /**
     * 
     * Currently the chat is lost whenever the user changes to another page
     * We oculd use localStorage to temporarly store the chat history
     * and we could add a start new session button to clear the localStorage 
     * 
     */

    return (
        <div className={styles.chatComponent} >

            <div>
                {messages.map(msg => (
                    <div key={msg.id}>
                        <p>{msg.sender}: {msg.text}</p>
                    </div>
                ))}
            </div>


            <div className={styles.chatBox}><ChatInput onSendMessage={handleSendMessage} /></div>

        </div>

    );
}

module.exports = ChatComponent;