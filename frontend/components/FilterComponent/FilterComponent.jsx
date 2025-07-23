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

  const filterGroups = [
    {
      title: "Geofences",
      options: ["Geofence 1", "Geofence 2", "Downtown ", "Norths"]
    },
    {
      title: "Fleets",
      options: ["Fleet 1", "Fleet 2", "Fleet 3"]
    },
    {
      title: "Time",
      options: ["Last 30 min", "Last hour", "Last 24 hrs"]
    }
  ];

  const fleetInputs = [
    {
      dataLgId: "fleet-1",
      label: fleet1Name,
      value: fleet1Capacity,
      onChange: (value) => dispatch(setFleet1Capacity(value.target.value))
    },
    {
      dataLgId: "fleet-2",
      label: fleet2Name,
      value: fleet2Capacity,
      onChange: (value) => dispatch(setFleet2Capacity(value))
    },
    {
      dataLgId: "fleet-3",
      label: fleet3Name,
      value: fleet3Capacity,
      onChange: (value) => dispatch(setFleet3Capacity(value.target.value))
    }
  ];

  const agentRunDocuments = [
    {
      title: "Agent Sessions",
      description: "Contains session metadata and the thread ID."
    },
    {
      title: "Historial Recommendations",
      description: "Contains a query to other relevant questions to the selected message"
    },
    {
      title: "Agent Profile",
      description: "This contains the identity of the agent, including instructions, goals and constraints."
    },
    {
      title: "Telemetry Data",
      description: "Contains the telemetry data queried to answer this question."
    },
    {
      title: "Queries",
      description: "Contains the queries made to the database during the agent's execution."
    },
    {
      title: "Logs",
      description: "Contains the logs generated during the agent's execution."
    },
    {
      title: "Last Checkpoint",
      description: "Contains the last checkpoint data for the agent's execution."
    }
  ];

  return (
    <div className={styles.filterComponent}>
      {/* First ExpandableCard with 3x 2x2 checkbox groups */}
      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Filters"
          description="This filters will apply to the conversation with the Leafy Fleet assistant."
          flagText=""
          darkMode={false}
        >
          <div className={styles.filterGrid}>
            {filterGroups.map((group, i) => (
              <div key={group.title} className={styles.checkboxGroup}>
                <h3 className={styles.groupTitle}>{group.title}</h3>
                {group.options.map((option, j) => (
                  <Checkbox key={option} data-lgid={`cb-${i * 4 + j + 1}`} label={option} />
                ))}
              </div>
            ))}
          </div>
        </ExpandableCard>
      </div>

      {/* Additional cards with just description */}
      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Fleet Overview"
          description="Here you can customize your current fleet."
          flagText=""
          darkMode={false}
        >
          <div className={styles.filterGrid}>
            {fleetInputs.map(input => (
              <NumberInput
                key={input.dataLgId}
                data-lgid={input.dataLgId}
                label={input.label}
                min={0}
                max={100}
                defaultValue={input.value}
                unit="vehicles"
                disabled={true}
                onChange={input.onChange}
              />
            ))}
          </div>
        </ExpandableCard>
      </div>

      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Agent Run Documents"
          description="This contains detailed information of the entire workflow performed by the agent to generate a specific response. Feel free to try out, and discover how we use AI inside of MongoDB to empower the user."
          flagText=""
          darkMode={false}
        >
          <div style={{ overflowY: "auto", maxHeight: "500px" }}>
            {agentRunDocuments.map((doc, idx) => (
              <div key={doc.title}>
                <Body baseFontSize={16}><strong>{doc.title}</strong></Body>
                <Body baseFontSize={14}>{doc.description}</Body>
                <Code language="javascript">{jsSnippet}</Code>
              </div>
            ))}
          </div>
        </ExpandableCard>
      </div>
    </div>
  );
};

export default FilterComponent;
