"use client"


import styles from './ChatInput.module.css'
import TextInput from '@leafygreen-ui/text-input';
import Button from "@leafygreen-ui/button";
import Icon from "@leafygreen-ui/icon";
import FollowUpQuestionsComponent from '@/components/FollowUpQuestionsComponent/FollowUpQuestionsComponent';
import { useDispatch, useSelector } from 'react-redux';
import { useState, useRef } from 'react';


/**
 * 
 * Currently the chat is lost whenever the user changes to another page
 * We oculd use localStorage to temporarly store the chat history
 * and we could add a start new session button to clear the localStorage 
 * 
 */

const ChatInput = ({ onSendMessage }) => {
    const [value, setValue] = useState('');

    const isLoadingAnswer = useSelector(state => state.Message.chatbotIsThinking);

    const sendMessage = (text) => {
        // console.log("Sending message:", text);
        // const messageText = text.trim();
        if (text) {
            onSendMessage(text);
            setValue('');
        }
    };
    const handleSubmit = (event) => {
        // console.log("Submit event:", value);
        // event.preventDefault();
        sendMessage(value);
    };

    const handleSuggestion = (index) => {
        sendMessage(FOLLOWUP_QUESTIONS[index]);
    };
    
    const askInputRef = useRef(null);



    const FOLLOWUP_QUESTIONS = [
        "If I wish to reduce my fleet size by 10%, what vehicles I should retire first and why?",
        "What are the top three types of maintenance scheduled across my fleet?",
        "Can I skip the next scheduled maintenance for carId 8?",
    ];

    return (
        <>
            <div>

                <FollowUpQuestionsComponent handleSuggestion={handleSuggestion} questions={FOLLOWUP_QUESTIONS} />


            </div>
            <div className={styles.chatInput} >
                {/* This component dosent want to use all of the avaliable width */}
                <TextInput
                    ref={askInputRef}
                    aria-labelledby='chat'
                    aria-label="Chat input"
                    placeholder="Ask me anything!"
                    onChange={e => {
                        setValue(e.target.value);
                    }}
                    onKeyDown={(e) => {
                        // console.log("Key pressed:", e.key);
                        if (e.key === 'Enter') {
                            handleSubmit();
                        }
                    }}
                    value={value}
                    className={styles.inputText}>
                </TextInput>
                <Button style={{ width: '100px' }} onClick={handleSubmit} variant="baseGreen" disabled={!askInputRef.current?.value.length === 0 || isLoadingAnswer}>
                    {isLoadingAnswer ? "Asking..." : "Ask"}
                </Button>


            </div>
        </>

    );
}

module.exports = ChatInput;