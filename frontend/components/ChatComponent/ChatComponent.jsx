"use client"

import styles from './ChatComponene.module.css'
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import ChatInput from '@/components/ChatInput/ChatInput';
import { useState, useRef, useEffect } from 'react';
import TextBubbleComponent from '@/components/TextBubbleComponent/TextBubbleComponent';
import { useDispatch, useSelector } from 'react-redux';
import { pushMessageHistory, setIsChatbotThinking } from '@/redux/slices/MessageSlice';



const ChatComponent = () => {

    const bottomRef = useRef(null);

    const lastMessageId = useSelector(state => state.Message.lastMessageId);
    
    
    const dispatch = useDispatch()
    const messages = useSelector(state => state.Message.messageHistory)
    const user = useSelector(state => state.User.name)

    const isLoadingAnswer = useSelector(state => state.Message.chatbotIsThinking);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (userMessageText) => {
        
        console.log("user", user)
        const newUserMessage = {
            id: lastMessageId + 1,
            text: userMessageText,
            sender: 'user',
            completed: true
        };

        console.log("newUserMessage", newUserMessage)

        dispatch(pushMessageHistory({message: newUserMessage, id: newUserMessage.id}));
        

        dispatch(setIsChatbotThinking(true));
        
        const botResponseMessage = {
            id: lastMessageId + 2,
            text: "This is a placeholder response from the bot.",
            sender: 'bot',
            completed: false
        };
        setTimeout(() => {
            dispatch(pushMessageHistory({ message: botResponseMessage, id: botResponseMessage.id }));
            
        }, 1000); // 1000 milliseconds = 1 second delay
        dispatch(setIsChatbotThinking(false));
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