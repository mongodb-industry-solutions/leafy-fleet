"use client";
import ExpandableCard from "@leafygreen-ui/expandable-card";
import Checkbox, { getTestUtils } from "@leafygreen-ui/checkbox";
import styles from "./FilterComponent.module.css";
import Code from "@leafygreen-ui/code";
import {
  H1,
  H2,
  Subtitle,
  Body,
  InlineCode,
  InlineKeyCode,
  Disclaimer,
  Overline,
  Link,
  BackLink,
} from "@leafygreen-ui/typography";
import { NumberInput } from "@leafygreen-ui/number-input";
import { useDispatch, useSelector } from "react-redux";
import {
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
} from "@/redux/slices/UserSlice";
const FilterComponent = () => {
  const dispatch = useDispatch();
  const {
    fleet1Capacity,
    fleet2Capacity,
    fleet3Capacity,
    fleet1Name,
    fleet2Name,
    fleet3Name,
  } = useSelector((state) => ({
    fleet1Capacity: state.User.fleet1Capacity,
    fleet2Capacity: state.User.fleet2Capacity,
    fleet3Capacity: state.User.fleet3Capacity,
    fleet1Name: state.User.fleet1Name,
    fleet2Name: state.User.fleet2Name,
    fleet3Name: state.User.fleet3Name,
  }));

  console.log("Fleet capacities from Redux state:", {
    fleet1Capacity,
    fleet2Capacity,
    fleet3Capacity,
  });

  // Snippet taken from https://www.mongodb.design/component/code/live-example
  const jsSnippet = `
    import datetime from './';

    const myVar = 42;

    var myObj = {
      someProp: ['arr', 'ay'],
      regex: /([A-Z])\w+/
    }

    export default class myClass {
      constructor(){
        // access properties
        this.myProp = false
      }
    }

    function greeting(entity) {
      return \`Hello, \${entity}! Cras justo odio, dapibus ac facilisis in, egestas eget quam. Vestibulum id ligula porta felis euismod semper.\`;
    }
    
    console.log(greeting('World'));
    `;

  return (
    <div className={styles.filterComponent}>
      {/* First ExpandableCard with 3x 2x2 checkbox groups */}
      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Filters"
          description=""
          flagText=""
          darkMode={false}
        >
          <div className={styles.filterGrid}>
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Geofencing</h3>
              <Checkbox data-lgid="cb-1" label="Geofence 1" />
              <Checkbox data-lgid="cb-2" label="Geofence 2" />
              <Checkbox data-lgid="cb-3" label="Downtown " />
              <Checkbox data-lgid="cb-4" label="Norths" />
            </div>
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Fleet Filter</h3>
              <Checkbox data-lgid="cb-5" label="Fleet 1" />
              <Checkbox data-lgid="cb-6" label="Fleet 2" />
              <Checkbox data-lgid="cb-7" label="Fleet 3" />
            </div>
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Time</h3>
              <Checkbox data-lgid="cb-8" label="All time" />
              <Checkbox data-lgid="cb-9" label="Last hour" />
            </div>
          </div>
        </ExpandableCard>
      </div>

      {/* Additional cards with just description */}
      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Fleet Overview"
          description=""
          flagText=""
          darkMode={false}
        >
          <div className={styles.filterGrid}>
            <NumberInput
              data-lgid="fleet-1"
              label={fleet1Name}
              min={0}
              max={100}
              defaultValue={fleet1Capacity}
              unit="vehicles"
              disabled={true}
              onChange={(value) =>
                dispatch(setFleet1Capacity(value.target.value))
              }
            />

            <NumberInput
              data-lgid="fleet-2"
              label={fleet2Name}
              min={0}
              max={100}
              defaultValue={`None` ? fleet2Capacity : `None`}
              unit="vehicles"
              disabled={true}
              onChange={(value) => dispatch(setFleet2Capacity(value))}
            />

            <NumberInput
              data-lgid="fleet-3"
              label={fleet3Name}
              min={0}
              max={100}
              defaultValue={fleet3Capacity}
              unit="vehicles"
              disabled={true}
              onChange={(value) =>
                dispatch(setFleet3Capacity(value.target.value))
              }
            />
          </div>
        </ExpandableCard>
      </div>

      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Agent Run Documents"
          description=""
          flagText=""
          darkMode={false}
        >
          <div style={{ overflowY: "auto", maxHeight: "500px" }}>
            <div>
              <Body baseFontSize={16}>agent_sessions</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>historial recommendations</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>agent profile</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>telemetry_data</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>queries</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>logs</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>last_checkpoint</Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
          </div>
        </ExpandableCard>
      </div>
    </div>
  );
};

export default FilterComponent;
