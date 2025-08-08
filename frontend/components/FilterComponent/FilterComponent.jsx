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
  const isSelected = useSelector((state) => state.Message.selectedMessage);
  const message = useSelector((state) =>
    state.Message.messageHistory.find((msg) => msg.id === isSelected?.id)
  );

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
  console.log("Selected Message:", isSelected);
  console.log("Message Data:", message);

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
                onChange={(e) => setFilter("downtown", e.target.checked)}
                label="Downtown"
              />
              <Checkbox
                onChange={(e) => setFilter("utxa", e.target.checked)}
                label="University of Texas at Austin"
              />
              <Checkbox
                onChange={(e) => setFilter("north_austin", e.target.checked)}
                label="North Austin"
              />
              <Checkbox
                onChange={(e) => setFilter("capitol_area", e.target.checked)}
                label="Capitol Area"
              />
              <Checkbox
                onChange={(e) => setFilter("south_austin", e.target.checked)}
                label="South Austin"
              />
              <Checkbox
                onChange={(e) => setFilter("east_austin", e.target.checked)}
                label="East Austin"
              />
              <Checkbox
                onChange={(e) => setFilter("west_austin", e.target.checked)}
                label="West Austin"
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
                <strong>Agent Profiles</strong>
              </Body>
              <Body baseFontSize={14}>
                Contains information about the agent's behavior and decisions.
              </Body>
              <Code language="javascript">
                {message != null && message.agent_profiles
                  ? typeof message.agent_profiles === "string"
                    ? message.agent_profiles
                    : JSON.stringify(message.agent_profiles, null, 2)
                  : "Select a message"}
              </Code>
            </div>
            <div>
              <Body baseFontSize={16}>Historial Data</Body>
              <Body baseFontSize={14}>
                Contains information from telemetry and other data sources to
                formulate the response.
              </Body>
              <Code language="javascript">
                {message != null && message.recommendation_data
                  ? typeof message.recommendation_data === "string"
                    ? message.recommendation_data
                    : JSON.stringify(message.recommendation_data, null, 2)
                  : "Select a message"}
              </Code>
            </div>
            <div>
              <Body baseFontSize={16}>Used tools</Body>
              <Body baseFontSize={14}>
                Tools used by the agent during the execution.
              </Body>
              <Code language="javascript">
                {message != null && message.used_tools
                  ? typeof message.used_tools === "string"
                    ? message.used_tools
                    : JSON.stringify(message.used_tools, null, 2)
                  : "Select a message"}
              </Code>
            </div>
            <div>
              <Body baseFontSize={16}>Last Checkpoint</Body>
              <Body baseFontSize={14}>
                Contains the last checkpoint data for the agent's execution.
              </Body>
              <Code language="javascript">
                {message != null && message.checkpoint
                  ? typeof message.checkpoint === "string"
                    ? message.checkpoint
                    : JSON.stringify(message.checkpoint, null, 2)
                  : "Select a message"}
              </Code>
            </div>
          </div>
        </ExpandableCard>
      </div>
    </div>
  );
};
export default FilterComponent;
