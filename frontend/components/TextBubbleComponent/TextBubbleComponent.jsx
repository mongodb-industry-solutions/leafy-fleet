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
  // console.log("userID", userID);
  const dispatch = useDispatch();
  const isSelected = useSelector((state) => state.Message.selectedMessage);

  return (
    <div className={`${styles.chatContainer}`}>
      <div
        className={`${styles.speechBubble} ${
          user === "user" ? styles.userBubble : styles.answerBubble
        }`}
        style={isSelected.id === id ? { background: "#F9EBFF" } : {}}
      >
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
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
        ) : (
          <Typewriter text={text} role={user} />
        )}
        {user === "bot" && (
          <Tooltip
            trigger={
              <IconButton
                aria-label="Select message"
                onClick={() => {
                  dispatch(setSelectedMessage({ message: { user, text, id } }));
                }}
              >
                {/* There are all the avaliable glyphs https://github.com/mongodb/leafygreen-ui/tree/ee7d80d450b652836d18edbf5682518fafc57d14/packages/icon/src/glyphs */}
                <Icon glyph={"Cursor"} />
              </IconButton>
            }
          >
            Select this message to see whats going on behind the scenes!
          </Tooltip>
        )}
      </div>
    </div>
  );
};

module.exports = TextBubbleComponent;
