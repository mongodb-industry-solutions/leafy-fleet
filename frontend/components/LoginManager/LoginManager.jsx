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
import Checkbox, { getTestUtils } from "@leafygreen-ui/checkbox";

import {
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
  setFleet1Name,
  setFleet2Name,
  setFleet3Name,
} from "@/redux/slices/UserSlice";
import { Option, OptionGroup, Select, Size } from "@leafygreen-ui/select";
import Button from "@leafygreen-ui/button";
import Code from "@leafygreen-ui/code";

const LoginManager = () => {
  const dispatch = useDispatch();
  const isSelectedUser = useSelector(
    (state) => state.User.selectedUser.userName
  );

  // Used to know if default value is needed
  const fleet1Size = useSelector((state) => state.User.fleet1Capacity) === 0

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

  const [open, setOpen] = useState(false);
  const [selectedFleets, setSelectedFleets] = useState(1);

  // Show how many fleet boxes to render based on user selection in the fleet selector
  const handleFleetChange = (value) => {
    setSelectedFleets(parseInt(value, 10)); // Update state with the selected value
  };

  // Used to manage opening and closing the fleet configuration modal
  const modalObserver = () => {
    if (isSelectedUser === "Kicho") {
      dispatch(setSelectedUser({ user: "Kicho" }));
      setOpen(true);
    } else {
      setOpen(false);
      dispatch(setSelectedUser({ user: "Frida" }));
      dispatch(setFleet1Capacity(50));
      dispatch(setFleet2Capacity(50));
      dispatch(setFleet3Capacity(50));
    }
  };

  const handleClose = () => {
    setOpen(false);
    if (fleet1Size == 0) {
      dispatch(setFleet1Capacity(20));
    }
  };

  return (
    <>
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
                  label="Select your City"
                  description="Select in what city will this simulation take place"
                  placeholder="Austin, TX"
                  name="City Selector"
                  size={Size.Default}
                  defaultValue="1"
                >
                  <Option value="New York" disabled="true">
                    New York, NY
                  </Option>
                  <Option value="Mexico City" disabled="true">
                    Mexico City, MX
                  </Option>
                  <Option value="Sao Paulo" disabled="true">
                    São Paulo, BR
                  </Option>
                </Select>
                <br />
                <Select
                  label="Select your number of fleets"
                  description="Select how many fleets will this simulation use"
                  placeholder="1"
                  name="Fleet Selector"
                  size={Size.Default}
                  defaultValue="1"
                  onChange={(value) => handleFleetChange(value)}
                >
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
              <div className={styles.selectFleetContainer}>
                <Subtitle>Choose what parameters to report</Subtitle>
                <br />
                <div className={styles.selectGrid}>
                  <Checkbox data-lgid="oil-level" label="Oil level" checked />
                  <Checkbox data-lgid="gas-level" label="Gas level" checked />
                  <Checkbox
                    data-lgid="last-maintance"
                    label="Last maintance"
                    checked
                  />
                  <Checkbox
                    data-lgid="ambient-temperature"
                    label="Ambient temperature"
                  />
                  <Checkbox
                    data-lgid="temperature"
                    label="Temperature"
                    checked
                  />
                  <Checkbox data-lgid="oee" label="OEE" checked />
                  <Checkbox
                    data-lgid="gas-efficiency"
                    label="Gas efficiency"
                    checked
                  />
                  <Checkbox
                    data-lgid="distance-driven"
                    label="Distance driven"
                  />
                  <Checkbox
                    data-lgid="latitude"
                    label="Latitude"
                    disabled
                    checked
                  />
                  <Checkbox
                    data-lgid="performance"
                    label="Performance"
                    disabled
                    checked
                  />
                  <Checkbox
                    data-lgid="run-time"
                    label="Run Time"
                    disabled
                    checked
                  />
                  <Checkbox
                    data-lgid="longitude"
                    label="Longitude"
                    disabled
                    checked
                  />
                  <Checkbox
                    data-lgid="avaliability"
                    label="Avaliability"
                    disabled
                    checked
                  />
                  <Checkbox
                    data-lgid="quality"
                    label="Quality"
                    disabled
                    checked
                  />
                </div>
              </div>
              <div className={styles.selectFleetContainer}>
                <Code language="javascript">
                  {`           
session
{
"_id" ObjectId("64f8c1e2d4f3a5b6c7d8e9f0"), // Unique identifier for the session
"thread_id" tread_2134543253
"fleet": [[1,2,3],[10,111],[160,900]] // Each list in the array represents a fleet and each element in the lists represents the carID whose information this session is able to access
"createdOn": ${Date.now()}
"lastUsed": ${Date.now()} // The last time this session was used
}
                    `}
                </Code>
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
              <div>
                <Description>Fleet {index + 1} </Description>
                <div class="input-group">
                  <input
                    type="text"
                    aria-label="Fleet Name"
                    class="form-control"
                    placeholder="Fleet Name"
                    onChange={(value) =>
                      handleFleetNameChange(index + 1, value)
                    }
                  />
                  <input
                    type="number"
                    aria-label="Fleet quantity"
                    class="form-control"
                    placeholder="Fleet quantity"
                    min="0"
                    max="100"
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
              <Subtitle>Start Simulation!</Subtitle>
            </Button>
          </div>
        </Container>
      </Modal>
    </>
  );
};

module.exports = LoginManager;
