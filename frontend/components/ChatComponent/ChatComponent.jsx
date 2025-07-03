"use client"

import styles from './ChatComponene.module.css'
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import ChatInput from '@/components/ChatInput/ChatInput';
import { useState, useRef, useEffect } from 'react';
import TextBubbleComponent from '@/components/TextBubbleComponent/TextBubbleComponent';
import { useDispatch, useSelector } from 'react-redux';
import { pushMessageHistory } from '@/redux/slices/MessageSlice';


const initialMessage = {
    id: 'initial',
    text: 'Hello! I am your AI assistant. How can I help you today?',
    sender: 'bot'
};

let nextId = 1;

const ChatComponent = () => {

    const bottomRef = useRef(null);
    
    
    const dispatch = useDispatch()
    const messages = useSelector(state => state.Message.messageHistory)
    

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);


    const handleSendMessage = async (userMessageText) => {

        const newUserMessage = {
            id: nextId++,
            text: userMessageText,
            sender: 'user',
        };
        const botResponseMessage = {
            id: nextId++,
            text: "This is a placeholder response from the bot.",
            sender: 'bot',
        };
        dispatch(pushMessageHistory({message: newUserMessage}));
        dispatch(pushMessageHistory({message: botResponseMessage})); // testing response
        // console.log("User message added:", newUserMessage);

    }


    return (
        <div className={styles.chatComponent}>
            <div className={styles.messagesContainer}>
                {messages.map((msg) => (
                    <div key={msg.id}>
                        <TextBubbleComponent user={msg.sender} text={msg.text} id={msg.id} />
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>

            <div className={styles.chatBox}>
                <ChatInput onSendMessage={handleSendMessage} />
            </div>
        </div>
    );
}

module.exports = ChatComponent;