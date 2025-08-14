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
import { setLoggedFleet, setSelectedFleets, setFleet1Capacity, setFleet2Capacity, setFleet3Capacity, setSessionId } from "@/redux/slices/UserSlice";
import { setSelectedUser } from "@/redux/slices/UserSlice";



const LoginComp = ({ modalObserver }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(true);
  }, []);
  const [threadId, setThreadId] = useState("");
  
  const dispatch = useDispatch();  

  
  const pathname = usePathname(); // Get the current route  
  const pathsRequiringLogin = ["/chat", "/charts", "/overview"]; // Paths requiring login  
  
  const shouldShowLoginPopup = pathsRequiringLogin.includes(pathname);  

  const handleClose = () => {
    modalObserver();
    setOpen(false);
  };
  
  const handleRestore = async () => {
    try {
      const response = await fetch(`http://${process.env.NEXT_PUBLIC_SESSIONS_SERVICE_URL}/sessions/${threadId}`);

      if (!response.ok) {
        throw new Error('Session not found');
      }

      const data = await response.json();
      console.log("Restored session:", data);

      // Set session data in Redux
      dispatch(setSessionId({ sessionId: threadId }));
      dispatch(setSelectedUser({ name: "Restored User" }));
      dispatch(setLoggedFleet(true)); // This is what keeps you logged in      
      // Restore fleet configuration
      const fleetConfig = data.vehicle_fleet;
      dispatch(setSelectedFleets({ selectedFleets: fleetConfig.selected_fleets }));
      dispatch(setFleet1Capacity(fleetConfig.fleet_size[0] || 20));
      dispatch(setFleet2Capacity(fleetConfig.fleet_size[1] || 0));
      dispatch(setFleet3Capacity(fleetConfig.fleet_size[2] || 0));
      // Close modal after successful restore
      setOpen(false);

      // Call simulation service to start the session  
      try {  
          const simResponse = await fetch(`http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/sessions`, {  
            method: 'POST',  
            headers: {  
              'Content-Type': 'application/json',  
            },  
            body: JSON.stringify({  
              session_id: threadId,  
              range1: fleetConfig.fleet_size[0] || 20,  
              range2: fleetConfig.fleet_size[1] || 0,  
              range3: fleetConfig.fleet_size[2] || 0  
            })  
          });  
      
          if (!simResponse.ok) {  
            const errorData = await simResponse.json();  
            throw new Error(`Simulation service error: ${errorData.detail || simResponse.status}`);  
          }  
      
          const simData = await simResponse.json();  
          console.log("Simulation session started:", simData);  
            
      } catch (simError) {  
          console.error("Error starting simulation session:", simError);  
          // You might want to show a warning but not fail the entire restore process  
        }  
      //ModalObserver(); // Call modalObserver to complete the login process
     
    } catch (error) {
      console.error("Error restoring session:", error);
      // You might want to show an error message to the user here
    }
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
      keyboard={false}
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
              className="btn btn-outline-primary"
              type="button"
              id="button-addon1"
              onClick={handleRestore}
            >
              Restore!
            </button>
            <input
              type="text"
              className="form-control"
              value={threadId}
              onChange={(e) => setThreadId(e.target.value)}
              aria-label="Session restoration input"
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
