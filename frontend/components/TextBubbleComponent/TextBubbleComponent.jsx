"use client";
import styles from "./TextBubbleComponent.module.css";
import { setSelectedMessage } from "@/redux/slices/MessageSlice";
import Typewriter from "./Typewriter";
import { useDispatch, useSelector } from "react-redux";
import { Body } from "@leafygreen-ui/typography";
import Tooltip from "@leafygreen-ui/tooltip";
import IconButton from "@leafygreen-ui/icon-button";
import Icon from "@leafygreen-ui/icon";
const TextBubbleComponent = ({ user, text, id }) => {
  const userID = useSelector((state) => state.User.selectedUser);
  const dispatch = useDispatch();
  const isSelected = useSelector((state) => state.Message.selectedMessage);
  const chatbotIsThinking = useSelector(
    (state) => state.Message.chatbotIsThinking
  );

  const latestThought = useSelector((state) => state.Message.currentThought);
  // console.log(latestThought);
  const lastMessageId = useSelector((state) => state.Message.lastMessageId);
  const message = useSelector((state) =>
    state.Message.messageHistory.find((msg) => msg.id === id)
  );

  const thinkingMessageId = useSelector((state) => state.Message.thinkingMessageId);

  // console.log("Message ID:", id, "ThinkingMessageId:", thinkingMessageId, "ChatbotIsThinking:", chatbotIsThinking, "Latest Thought:", latestThought);

  return (
    <div className={`${styles.chatContainer}`}>
      <div
        className={`${styles.speechBubble} ${
          user === "user" ? styles.userBubble : styles.answerBubble
        }`}
        style={isSelected?.id === id ? { background: "#F9EBFF" } : {}}
      >
        <div className={user === "bot" ? styles.botHeader : styles.userHeader}>
          <img
            src={
              user === "bot"
                ? "/coachGTM_Headshot.png"
                : `/rsc/users/${userID._id}.png`
            }
            style={
              user === "bot"
                ? { alignSelf: "flex-start" }
                : { alignSelf: "flex-end" }
            }
            className={styles.imageStyling}
            alt="PFP"
          />
          <Body weight="medium">
            {user === "bot" ? "Assistant Bot" : userID.name}
          </Body>
        </div>

        <hr style={{ margin: "0px" }} />
        {user === "user" ? (
          <Body>{text}</Body>
        ) : id === thinkingMessageId && chatbotIsThinking && latestThought ? (
          <Body style={{ color: "#aaaaaa" }}>thoughts: {latestThought}</Body>
        ) : id === thinkingMessageId && !chatbotIsThinking && message?.text ? (
          <Typewriter text={message.text} role={user} id={id} />
        ) : (
          // For all other bot messages, just show the text
          <Body>{message?.text}</Body>
        )}
        {user === "bot" && id !== 0 && (
          <Tooltip
            trigger={
              <IconButton
                aria-label="Select message"
                onClick={() => {
                  dispatch(setSelectedMessage({ message: { user, text, id } }));
                }}
              >
                <Icon glyph={"Visibility"} />
              </IconButton>
            }
          >
            Select this message to see what’s going on behind the scenes!
          </Tooltip>
        )}
      </div>
    </div>
  );
};

export default TextBubbleComponent;
