"use client"


import styles from './ChatInput.module.css'
import TextInput from '@leafygreen-ui/text-input';
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";

import { useState } from 'react';




const ChatInput = ({ onSendMessage }) => {
    const [value, setValue] = useState('');

    const handleSubmit = (event) => {
        console.log("Submit event triggered");
        console.log("Current input value:", value);
        event.preventDefault();
        const messageText = value.trim();

        if (messageText) {
            onSendMessage(messageText);
            setValue('');
        }
    };


    return (
        <>
            <div className={styles.chatInput} >
                {/* This component dosent want to use all of the avaliable width */}         
                    <TextInput
                    label='chat'
                        placeholder="Ask me anything!"
                        onChange={e => {
                            setValue(e.target.value);
                        }}
                        value={value}
                        
                    >
                    </TextInput>
                    <Button style={{ width: '100px' }} onClick={handleSubmit} >
                        Send!
                    </Button>
               

            </div>
        </>

    );
}

module.exports = ChatInput;