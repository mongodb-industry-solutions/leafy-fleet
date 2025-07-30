"use client";

/**
 * This component only manages the user selection modal
 * To see the fleet configuration modal, see LoginManager.jsx
 */

import React, { useState, useEffect } from "react";
import { Modal, Container } from "react-bootstrap";
import { H2, Subtitle, Description } from "@leafygreen-ui/typography";

import styles from "./loginComp.module.css";
import UserComp from "../user/UserComp";
import Banner from "@leafygreen-ui/banner";
import WizardIcon from "@leafygreen-ui/icon/dist/Wizard";
import { USER_MAP } from "@/lib/constants";
import { useDispatch, useSelector } from "react-redux";
import { usePathname } from "next/navigation";
import {
  setLoggedFleet} from "@/redux/slices/UserSlice";
const LoginComp = ({ modalObserver }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(true);
  }, []);

  
  const dispatch = useDispatch();  

  
  const pathname = usePathname(); // Get the current route  
  const pathsRequiringLogin = ["/chat", "/charts", "/overview"]; // Paths requiring login  
  
  const shouldShowLoginPopup = pathsRequiringLogin.includes(pathname);  

  const handleClose = () => {
    modalObserver();
    setOpen(false);
  };
  

  if (shouldShowLoginPopup) {  
    return (  
    <Modal
      show={open}
      onHide={handleClose}
      size="lg"
      aria-labelledby="contained-modal-title-vcenter"
      centered
      fullscreen={"md-down"}
      className={styles.leafyFeel}
      backdrop="static"
    >
      <Container className="p-3 h-100">
        {/*
                <div className='d-flex flex-row-reverse p-1 cursorPointer' onClick={handleClose}>
                    <Icon glyph="X" />
                </div>
               */}

        <div className={styles.modalMainCOntent}>
          <H2 className={styles.centerText}>Welcome to Leafy Fleet</H2>
          <Subtitle
            className={`${styles.weightNormal} ${styles.centerText} mt-2`}
          >
            This is a MongoDB demo
          </Subtitle>
          <br />
          <Description className={styles.descriptionModal}>
            Please select the user you would like to login as
          </Description>
          <br />
          <div className="input-group mb-3">
            <button
              className="btn btn-outline-primary "
              type="button"
              id="button-addon1"

            >
              Restore!
            </button>
            <input
              type="text"
              class="form-control"
              aria-label="Example text with button addon"
              aria-describedby="button-addon1"
              placeholder="If you have a valid thread_id, you can restore your session here!"
            />
          </div>
          <div className={`${styles.usersContainer}`}>
            {USER_MAP.map((user, index) => (
              <UserComp
                key={index}
                user={user}
                handleClose={handleClose}
              ></UserComp>
            ))}
          </div>
          <Banner variant="info" className="mb-2">
            Look out for <WizardIcon></WizardIcon> to find out more about what
            is going on behind the scenes!
          </Banner>
          <Description className={`${styles.descriptionModal} mb-3`}>
            Note: Demo to display MongoDb's use cases of time series with fleet managment.
          </Description>
        </div>
      </Container>
    </Modal>
  );
}
return null; // If the current route does not require login, return null
};

export default LoginComp;
