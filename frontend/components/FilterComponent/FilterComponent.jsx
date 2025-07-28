"use client";
import ExpandableCard from "@leafygreen-ui/expandable-card";
import Checkbox from "@leafygreen-ui/checkbox";
import styles from "./FilterComponent.module.css";
import Code from "@leafygreen-ui/code";
import { Body } from "@leafygreen-ui/typography";
import { NumberInput } from "@leafygreen-ui/number-input";
import { useDispatch, useSelector } from "react-redux";
import {
  setFleet1Capacity,
  setFleet2Capacity,
  setFleet3Capacity,
  setQueryFilters,
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

  const setFilter = (label, checked) => {
    dispatch(setQueryFilters({ label, checked }));
  };

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
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Geofences</h3>
              <Checkbox
                onChange={(e) => setFilter("Geofence 1", e.target.checked)}
                label="Geofence 1"
              />
              <Checkbox
                onChange={(e) => setFilter("Geofence 2", e.target.checked)}
                label="Geofence 2"
              />
              <Checkbox
                onChange={(e) => setFilter("Downtown", e.target.checked)}
                label="Downtown"
              />
              <Checkbox
                onChange={(e) => setFilter("North", e.target.checked)}
                label="North"
              />
            </div>
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Fleets</h3>
              {fleet1Name && (
                <Checkbox
                  onChange={(e) => setFilter("Fleet 1", e.target.checked)}
                  label={fleet1Name}
                />
              )}
              {fleet2Name && (
                <Checkbox
                  onChange={(e) => setFilter("Fleet 2", e.target.checked)}
                  label={fleet2Name}
                />
              )}
              {fleet3Name && (
                <Checkbox
                  onChange={(e) => setFilter("Fleet 3", e.target.checked)}
                  label={fleet3Name}
                />
              )}
            </div>
            <div className={styles.checkboxGroup}>
              <h3 className={styles.groupTitle}>Time</h3>
              <Checkbox
                onChange={(e) => setFilter("Last 30 min", e.target.checked)}
                label="Last 30 min"
              />
              <Checkbox
                onChange={(e) => setFilter("Last hour", e.target.checked)}
                label="Last hour"
              />
              <Checkbox
                onChange={(e) => setFilter("Last 2 hours", e.target.checked)}
                label="Last 2 hours"
              />
            </div>
          </div>
        </ExpandableCard>
      </div>
      {/* Additional cards with just description */}
      <div className={styles.cardWrapper}>
        <ExpandableCard
          title="Fleet Overview"
          description="Here you can overview your current fleet."
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
          description="This contains detailed information of the entire workflow performed by the agent to generate a specific response. Feel free to try out, and discover how we use AI inside of MongoDB to empower the user."
          flagText=""
          darkMode={false}
        >
          <div style={{ overflowY: "auto", maxHeight: "500px" }}>
            <div>
              <Body baseFontSize={16}>
                <strong>Agent Sessions</strong>
              </Body>
              <Body baseFontSize={14}>
                Contains session metadata and the thread ID.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Historial Recommendations</Body>
              <Body baseFontSize={14}>
                Contains a query to other relevant questions to the selected
                message
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Agent Profile</Body>
              <Body baseFontSize={14}>
                This contains the identity of the agent, including instructions,
                goals and constraints.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Telemetry Data</Body>
              <Body baseFontSize={14}>
                Contains the telemetry data queried to answer this question.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Queries</Body>
              <Body baseFontSize={14}>
                Contains the queries made to the database during the agent's
                execution.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Logs</Body>
              <Body baseFontSize={14}>
                Contains the logs generated during the agent's execution.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
            <div>
              <Body baseFontSize={16}>Last Checkpoint</Body>
              <Body baseFontSize={14}>
                Contains the last checkpoint data for the agent's execution.
              </Body>
              <Code language="javascript">{jsSnippet}</Code>
            </div>
          </div>
        </ExpandableCard>
      </div>
    </div>
  );
};
export default FilterComponent;
