"use client";
import styles from "./TextBubbleComponent.module.css";
import { setSelectedMessage } from "@/redux/slices/MessageSlice";
import Typewriter from "./Typewriter";
import { useSelector } from "react-redux";
import { Body } from "@leafygreen-ui/typography";
const TextBubbleComponent = ({ user, text }) => {

    const userID = useSelector(state => state.User.selectedUser);
    console.log("userID", userID)

  return (
    <div className={`${styles.chatContainer}`}>
      
      <div
        className={`${styles.speechBubble} ${
          user === "user"
            ? styles.userBubble
            : styles.answerBubble
        }`}
      >
        <div style={{display: "flex", gap: "10px",  alignItems: "center"}}>
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
      
        
        <hr style={{margin: "0px"}}/>
        {user === "user" ? (
          <Body>{text}</Body>
        ) : (
          <Typewriter text={text} role={user} />
        )}
      </div>
      {/* <img
        src="/Eye_icon.png"
        width={"50px"}
        height={"50px"}
        alt="Eye icon"
        style={
          user === "bot"
            ? { alignSelf: "flex-start", marginLeft: "10px", cursor: "pointer" }
            : { display: "none" }
        }
        onClick={() => {
          dispatch(setSelectedMessage({ message: { user, text, id } }));
        }}
      /> */}
    </div>
  );
};

module.exports = TextBubbleComponent;
