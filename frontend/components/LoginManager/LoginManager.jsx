"use client";

import { useDispatch, useSelector } from "react-redux";
import LoginComp from "../login/LoginComp";
import styles from "./LoginManager.module.css";
import { setSelectedUser } from "@/redux/slices/UserSlice";
import React, { useState, useEffect } from "react";
import { Modal, Container } from "react-bootstrap";
import { H1, H2, Subtitle, Description } from "@leafygreen-ui/typography";
import { NumberInput } from "@leafygreen-ui/number-input";
import Checkbox, { getTestUtils } from "@leafygreen-ui/checkbox";

import { setFleet1Capacity, setFleet2Capacity, setFleet3Capacity } from "@/redux/slices/UserSlice";
import { Option, OptionGroup, Select, Size } from "@leafygreen-ui/select";
import Button from "@leafygreen-ui/button";
import Code from "@leafygreen-ui/code";

const LoginManager = () => {
  const dispatch = useDispatch();
  const isSelectedUser = useSelector(
    (state) => state.User.selectedUser.userName
  );

  const { fleet1Capacity, fleet2Capacity, fleet3Capacity } = useSelector(
    (state) => ({
      fleet1Capacity: state.User.fleet1Capacity,
      fleet2Capacity: state.User.fleet2Capacity,
      fleet3Capacity: state.User.fleet3Capacity,
    })
  );

  const [open, setOpen] = useState(false);

  // console.log("LoginManager isSelectedUser", isSelectedUser)

  const modalObserver = () => {
    if (isSelectedUser === "Kicho") {
      setOpen(true);
    }
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleNumberPlacement = (value) => {
    console.log("Number of vehicles per fleet:", value);
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
                >
                  <Option value="2">2</Option>
                  <Option value="3">3</Option>
                </Select>
                <br />
                <NumberInput
                  data-lgid="fleet-2"
                  label="Number of vehicles per fleet"
                  min={0}
                  max={100}
                  defaultValue={"Custom"}
                  unit="vehicles"
                  style={{ width: "180px" }}
                  placeholder="Custom"
                />
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
            <NumberInput
              data-lgid="fleet-1"
              label="Fleet 1"
              min={0}
              max={100}
              defaultValue={50}
              unit="vehicles"
              onChange={(value) => dispatch(setFleet1Capacity({ capacity: value }))}
            />

            <NumberInput
              data-lgid="fleet-2"
              label="Fleet 2"
              min={0}
              max={100}
              defaultValue={50}
              unit="vehicles"
                onChange={(value) => dispatch(setFleet2Capacity({ capacity: value }))}
            />

            <NumberInput
              data-lgid="fleet-3"
              label="Fleet 3"
              min={0}
              max={100}
              defaultValue={50}
              unit="vehicles"
              onChange={(value) => dispatch(setFleet3Capacity({ capacity: value }))}
            />
          </div>
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
