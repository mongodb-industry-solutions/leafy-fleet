"use client";

import { useRef, useEffect, useState } from 'react';

import styles from './TextBubbleComponent.module.css'
import { setSelectedMessage } from '@/redux/slices/MessageSlice';
import { useDispatch, useSelector } from 'react-redux';

const TextBubbleComponent = ({ user, text, id }) => {

    const bubbleRef = useRef(null);
    const dispatch = useDispatch()
    const isSelected = useSelector(state => state.Message.selectedMessage?.id) == id

    return (
        <div className={`${styles.chatContainer}`}>

            <img
                src={user === 'bot' ? '/MongoDBLeafy.svg' : '/MongoDBLeafy.svg'}
                style={user === 'bot' ? { alignSelf: 'flex-start' } : { alignSelf: 'flex-end' }}
                alt="PFP"
                width="50px"
                height="50px"
            />
            <div style={{backgroundColor: isSelected ? '#00ED64': ''}} className={`${user === 'bot' ? styles.botBubble : styles.userBubble}`} ref={bubbleRef}>
                {text}
            </div>
            <img
                src="/Eye_icon.png"
                width={'50px'}
                height={'50px'}
                alt="Eye icon"
                style={user === 'bot' ? { alignSelf: 'flex-start', marginLeft: '10px', cursor: 'pointer' } : { display: 'none' }}
                onClick={() => {
                    dispatch(setSelectedMessage({message: { user, text, id }}))

                }}

            />

        </div>
    );










}


module.exports = TextBubbleComponent;