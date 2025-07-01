"use client";


import styles from './TextBubbleComponent.module.css'



const TextBubbleComponent = ({ user, text }) => {



    return (
        <div className={`${styles.chatContainer}`}>

            <img
                src={user === 'bot' ? '/MongoDBLeafy.svg' : '/MongoDBLeafy.svg'}
                style={user === 'bot' ? { alignSelf: 'flex-start' } : { alignSelf: 'flex-end' }}
                alt="PFP"
                width="50px"
                height="50px"
            />
            <div className={`${user === 'bot' ? styles.botBubble : styles.userBubble}`}>
                {text}
            </div>

        </div>
    );










}


module.exports = TextBubbleComponent;