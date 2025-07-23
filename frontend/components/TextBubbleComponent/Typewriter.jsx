"use client";

import { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setAnimationMessage } from "@/redux/slices/MessageSlice";
import { Body } from "@leafygreen-ui/typography";

const Typewriter = ({ text, role, id }) => {
  const isAnimationDone = useSelector(
    (state) => state.Message.messageHistory[id]?.completed
  );
  const typingIntervalRef = useRef(null);
  const dispatch = useDispatch();
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    if (isAnimationDone) {
      setDisplayedText(text);
      return;
    }

    if (role === "bot") {
      let currentIndex = 0;

      const typeNextCharacter = () => {
        currentIndex++;
        setDisplayedText((prev) => text.slice(0, currentIndex));

        if (currentIndex >= text.length) {
          clearInterval(typingIntervalRef.current);
          dispatch(setAnimationMessage({ id: id, completed: true }));
        }
      };

      // Speed up the typing by reducing the interval from 30ms to 10ms
      typingIntervalRef.current = setInterval(typeNextCharacter, 10);

      return () => clearInterval(typingIntervalRef.current);
    }
  }, [text, role, id, isAnimationDone, dispatch]);

  // Preserve newlines by replacing \n with <br />
  return (
    <Body
      dangerouslySetInnerHTML={{
        __html: displayedText.replace(/\n/g, "<br />"),
      }}
    />
  );
};

export default Typewriter;
