"use client";

/**
 * This component manages all of the login and user selection logic
 * The "traditional" user select as it appears on other demos is inside LoginComp.jsx
 * This component also manages the fleet configuration modal that appears when the right user is selected
 */

import { useDispatch, useSelector } from "react-redux";
import LoginComp from "../login/LoginComp";
import styles from "./LoginManager.module.css";
import { setSelectedUser } from "@/redux/slices/UserSlice";
import React, { useState, useEffect } from "react";
import { Modal, Container } from "react-bootstrap";
import { H1, H2, Subtitle, Description } from "@leafygreen-ui/typography";
import AttributesComponent from "../AttributesComponent/AttributesComponent";
import {
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
  setFleet1Name,
  setFleet2Name,
  setFleet3Name,
  setSelectedFleets,
  setEditFleet,
  setLoggedFleet
} from "@/redux/slices/UserSlice";
import { Option, Select, Size } from "@leafygreen-ui/select";
import Button from "@leafygreen-ui/button";
import { usePathname } from "next/navigation";   
import DocumentFleetComponent from "../DocumentFleetComponent/DocumentFleetComponent";

const LoginManager = () => {
  const dispatch = useDispatch();
  const selectedUser = useSelector(
    (state) => state.User.selectedUser
  );
  const editFleet = useSelector((state) => state.User.editFleet);

  const selectedFleets = useSelector((state) =>state.User.selectedFleets);

  // Used to know if default value is needed

  const fleet1Size = useSelector((state) => state.User.fleet1Capacity)
  const fleet2Size = useSelector((state) => state.User.fleet2Capacity)
  const fleet3Size = useSelector((state) => state.User.fleet3Capacity)
  const fleet1Name = useSelector((state) => state.User.fleet1Name);
  const fleet2Name = useSelector((state) => state.User.fleet2Name);
  const fleet3Name = useSelector((state) => state.User.fleet3Name);


  // Dispatch actions based on user input or component logic
  const dispatchFleetCapacity = (indexFleet, fleetCapacity) => {
    // console.log("Dispatching fleet capacity:", indexFleet, fleetCapacity);
    if (indexFleet === 1) {
      dispatch(setFleet1Capacity(fleetCapacity));
    } else if (indexFleet === 2) {
      dispatch(setFleet2Capacity(fleetCapacity));
    } else if (indexFleet === 3) {
      dispatch(setFleet3Capacity(fleetCapacity));
    }
  };

  const handleFleetCapacityChange = (indexFleet, fleetCapacity) => {
    console.log("Handling fleet capacity change:", indexFleet, fleetCapacity);
    dispatchFleetCapacity(indexFleet, fleetCapacity);
  };

  // Save fleet name to redux
  const dispatchFleetName = (indexFleet, fleetName) => {
    if (indexFleet === 1) {
      dispatch(setFleet1Name(fleetName));
    } else if (indexFleet === 2) {
      dispatch(setFleet2Name(fleetName));
    } else if (indexFleet === 3) {
      dispatch(setFleet3Name(fleetName));
    }
  };
  const handleFleetNameChange = (indexFleet, fleetName) => {
    dispatchFleetName(indexFleet, fleetName.target.value);

  };
  

  const isLoggedIn = useSelector((state) => state.User.isLoggedIn); 

  const [open, setOpen] = useState(false);

  // Show how many fleet boxes to render based on user selection in the fleet selector
  const handleFleetChange = (value) => {
    dispatch(setSelectedFleets({selectedFleets: value}))
  };

  // Used to manage opening and closing the fleet configuration modal
  const modalObserver = () => {
    if (selectedUser.name === "Kicho") {   
      setOpen(true);
    } else {
      setOpen(false);
      dispatch(setLoggedFleet(true)); 
      dispatch(setFleet1Capacity(20));
      dispatch(setFleet2Capacity(10));
      dispatch(setFleet3Capacity(20));
      dispatch(setFleet1Name("Fleet 1"));
      dispatch(setFleet2Name("Fleet 2"));
      dispatch(setFleet3Name("Fleet 3"));
      dispatch(setSelectedFleets({ selectedFleets: 3 }));

    }
  };

  const handleClose = () => {
    setOpen(false);
    dispatch(setLoggedFleet(true)); 
    if (fleet1Size == 0) {
      dispatch(setFleet1Capacity(20));
      dispatch(setFleet2Capacity(0));
      dispatch(setFleet3Capacity(0));
    }
    if(fleet1Name === ""){
      dispatch(setFleet1Name("Fleet 1"));
    }

  };

  const pathname = usePathname(); // Get the current route  
  const pathsRequiringLogin = ["/chat", "/charts", "/overview"]; // Paths requiring login  
  
  const shouldShowLoginPopup = pathsRequiringLogin.includes(pathname);  
  
  if (isLoggedIn) {  
    return null;  
  }

  if (shouldShowLoginPopup) {  
    return ( 
      <div>
      <LoginComp modalObserver={modalObserver} />

      <Modal
        show={open}
        onHide={handleClose}
        size="xl"
        aria-labelledby="contained-modal-title-vcenter"
        centered
        fullscreen="md-down"
        backdrop="static"
        className="flex"
        style={{ maxHeight: "800px" }}
      >
        <Container className="p-4">
          <div className="text-center p-2 bg-white cursor-pointer">
            <H1>Fleet configuration</H1>
          </div>
          <div className={styles.modalMainCOntent}>
            <div className={`${styles.usersContainer}`}>
              <div className={styles.selectFleetContainer}>
                <Subtitle>Select your fleet</Subtitle>
                <Select
                  label="Select your city"
                  description="Select in which city this simulation will take place."
                  name="City Selector"
                  size={Size.Default}
                  defaultValue="Austin"
                  allowDeselect={false}
                >
                  <Option value="Austin" disabled={false}>
                    Austin
                  </Option>
                  <Option value="NYC" disabled="true">
                    New York, NY
                  </Option>
                  <Option value="CDMX" disabled="true">
                    Mexico City, MX
                  </Option>
                  <Option value="SPLO" disabled="true">
                    São Paulo, BR
                  </Option>
                </Select>
                <br />
                <Select
                  label="Select your number of fleets"
                  description="Select how many fleets this simulation will have."
                  name="Fleet Selector"
                  size={Size.Default}
                  value={String(selectedFleets)}
                  onChange={handleFleetChange}
                  allowDeselect={false}
                >
                  <Option value="1">1</Option>
                  <Option value="2">2</Option>
                  <Option value="3">3</Option>
                </Select>
                <br />
               
                {/* <NumberInput
                  data-lgid="fleet-2"
                  label="Number of vehicles per fleet"
                  min={0}
                  max={100}
                  defaultValue={"Custom"}
                  unit="vehicles"
                  style={{ width: "180px" }}
                  placeholder="Custom"
                  onChange={(value) => console.log(`New value: ${value}`)}  
                  onBlur={(value) => console.log(`Final value: ${value}`)}  
                /> */}
                <br />
              </div>
              <AttributesComponent/>
             
              <div className={styles.selectFleetContainer}>
                <DocumentFleetComponent/>
              </div>
            </div>
          </div>
          
          <div
            className={styles.selectGrid}
            style={{
              marginTop: "20px",
              paddingLeft: "40px",
              paddingRight: "40px",
            }}
          >
            {Array.from({ length: selectedFleets }).map((_, index) => (
              <div onClick={() => {

                if (index === 0) {
                  dispatch(setEditFleet({ editFleet: 1 }));
                } else if (index === 1) {
                  dispatch(setEditFleet({ editFleet: 2 }));
                } else {
                  dispatch(setEditFleet({ editFleet: 3 }));
                }
              }}
              className={
                    editFleet === index + 1
                      ? `${styles.selectedFleetBox}`
                      : ""
                  }
              style={{ cursor: "pointer" }}
              key={index}
              >
                <Description className={styles.Desc}>Fleet {index + 1} </Description>
                <div className="input-group">
                  <input
                    type="text"
                    aria-label="Fleet Name"
                    className="form-control"
                    placeholder="Fleet Name"
                    onFocus={() => dispatch(setEditFleet({ editFleet: index + 1 }))}

                    onChange={(value) =>{
                      handleFleetNameChange(index + 1, value);
                                       
                    }}
                  />
                  <input
                    type="number"
                    aria-label="Fleet quantity"
                    className="form-control"
                    placeholder="Fleet quantity"
                    min="0"
                    max="100"
                    onFocus={() => dispatch(setEditFleet({ editFleet: index + 1 }))}
                    onChange={(e) => {
                      let value = parseInt(e.target.value, 10);
                      // If the parsed value is greater than 100, set it back to 100
                      if (value > 100) {
                        value = 100;
                        e.target.value = 100;
                      }

                      if (value < 0) {
                        value = 0;
                        e.target.value = 0;
                      }

                      // Handle cases where input is empty or not a valid number (e.g., after deleting all text)
                      if (isNaN(value)) {
                        value = 0; // Or null, depending on your desired default for empty
                      }

                      handleFleetCapacityChange(index + 1, value);
                      
                    }}
                  />
                  
                </div>
              </div>
            ))}
            
          </div>
          <Description style={{marginLeft: 50}}>If no value is selected, fleet 1 will have 20 vehicles</Description>
          <br />
          <div className="d-flex justify-content-center">
            <Button style={{ background: "#00ED64" }} onClick={handleClose}>
              Start Simulation!
            </Button>
          </div>
        </Container>
      </Modal>
    </div>
  );
}
  return null;  
  
};

module.exports = LoginManager;
