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
import { setLoggedFleet, setSelectedFleets, setFleet1Capacity, setFleet2Capacity, setFleet3Capacity, setSessionId , setFleet1Name, setFleet1Attributes, setFleet2Name, setFleet2Attributes, setFleet3Name, setFleet3Attributes} from "@/redux/slices/UserSlice";
import { setSelectedUser } from "@/redux/slices/UserSlice";
import { setGeofences } from "@/redux/slices/GeofencesSlice";  


const LoginComp = ({ modalObserver }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(true);
  }, []);
  const [threadId, setThreadId] = useState("");
  
  const dispatch = useDispatch();  

  useEffect(() => {  
    const fetchGeofences = async () => {  
      try {  
        const response = await fetch(`http://${process.env.NEXT_PUBLIC_GEOSPATIAL_SERVICE_URL}/geofences`);  
        if (!response.ok) {  
          throw new Error("Failed to fetch geofences");  
        }  
        const data = await response.json();  
        dispatch(setGeofences({ geofences: data.geofences })); // Fixed action name 
        //console.log("Fetched geofences:", data.geofences); 
        
        //console.log("Fetched geofences:", data.geofences);
      } catch (error) {  
        console.error("Error fetching geofences:", error);  
      }  
    }  
    fetchGeofences();  
  }, [dispatch]);  

  
  const pathname = usePathname(); // Get the current route  
  const pathsRequiringLogin = ["/chat", "/charts", "/geosearch"]; // Paths requiring login  
  
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
    dispatch(setLoggedFleet(true));          
      
    // Restore fleet configuration  
    const fleetConfig = data.vehicle_fleet;  
    dispatch(setSelectedFleets({ selectedFleets: fleetConfig.selected_fleets }));  
      
    // Use optional chaining and provide fallbacks  
    dispatch(setFleet1Capacity(fleetConfig.fleet_size?.[0] || 20));  
    dispatch(setFleet1Name(fleetConfig.fleet_names?.[0] || "Fleet 1"));  
    dispatch(setFleet1Attributes(fleetConfig.attribute_list?.[0] || []));   
      
    if (fleetConfig.fleet_size?.length > 1) {  
      dispatch(setFleet2Name(fleetConfig.fleet_names?.[1] || "Fleet 2"));  
      dispatch(setFleet2Capacity(fleetConfig.fleet_size?.[1] || 0));  
      dispatch(setFleet2Attributes(fleetConfig.attribute_list?.[1] || []));   
    }     
      
    if (fleetConfig.fleet_size?.length > 2) {  
      dispatch(setFleet3Name(fleetConfig.fleet_names?.[2] || "Fleet 3"));  
      dispatch(setFleet3Capacity(fleetConfig.fleet_size?.[2] || 0));  
      dispatch(setFleet3Attributes(fleetConfig.attribute_list?.[2] || []));  
    }  
      
    // Close modal after successful restore  
    setOpen(false);  

    //in case session does exist but not currently in 
    try {  
        // Get fleet configuration from Redux to use as fleetConfig  
        const fleetConfig = {  
          fleet_size: [  
            fleet1Capacity || 20,  
            fleet2Capacity || 10,  
            fleet3Capacity || 20  
          ]  
        };  
  
        const simResponse = await fetch(`http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/sessions`, {  
          method: 'POST',  
          headers: {  
            'Content-Type': 'application/json',  
          },  
          body: JSON.stringify({  
            session_id: sessionId, // Use sessionId from Redux  
            range1: fleetConfig.fleet_size[0] || 20,  
            range2: fleetConfig.fleet_size[1] || 10,  
            range3: fleetConfig.fleet_size[2] || 20  
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
            This is a demo showcasing MongoDB’s geospatial and time series capabilities for fleet management
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
          
        </div>
      </Container>
    </Modal>
  );
}
return null; // If the current route does not require login, return null
};

export default LoginComp;
