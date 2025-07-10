"use client";

import { Body, Description } from '@leafygreen-ui/typography';
import Card from '@leafygreen-ui/card';
import styles from './FollowUpQuestionsComponent.module.css'
import { useMemo } from 'react';


const FollowUpQuestionsComponent = ({ handleSuggestion, questions }) => {
    return (

        <div className={styles.suggestedQuestions}>
            <Body>Suggested Questions:</Body>
            {
                questions.map((suggestion, index) =>
                    <button key={`sug-${index}`} className={styles.suggestion} onClick={() => handleSuggestion(index)}>
                        <Description>{suggestion}</Description>
                    </button>
                )
            }
        </div>

    );


}

module.exports = FollowUpQuestionsComponent;