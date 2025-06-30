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

let nextId = 0;

const ChatComponent = () => {

    const [messages, setMessages] = useState(initialMessage);

    const handleSendMessage = async (userMessageText) => {
       
        const newUserMessage = {
            id: nextId++,
            text: userMessageText,
            sender: 'user',
        };
        setMessages(prev => [newUserMessage]);
        console.log("User message added:", newUserMessage);
    }


    return (
        <div className={styles.chatComponent} >

            {/* <div>
                {messages.map(msg => (
                    <div
                        key={msg.id}
                    >
                        <p>{msg.text}</p>
                    </div>
                ))}
            </div> */}


            <div className={styles.chatBox}><ChatInput onSendMessage={handleSendMessage}/></div>

        </div>

    );
}

module.exports = ChatComponent;