import { useSelector, useDispatch } from "react-redux";
import { setFleet1Attributes, setFleet2Attributes, setFleet3Attributes } from "@/redux/slices/UserSlice";
import Checkbox from "@leafygreen-ui/checkbox";
import styles from "./AttributesComponent.module.css";
import { Subtitle } from "@leafygreen-ui/typography";

const ALL_ATTRIBUTES = [
  "Oil level",
  "Gas level",
  "Last maintance",
  "Ambient temperature",
  "Temperature",
  "OEE",
  "Gas efficiency",
  "Distance driven",
  "Latitude",
  "Performance",
  "Run Time",
  "Longitude",
  "Avaliability",
  "Quality"
];

const ATTR_KEY_MAP = {
  "Oil level": "oil-level",
  "Gas level": "gas-level",
  "Last maintance": "last-maintance",
  "Ambient temperature": "ambient-temperature",
  "Temperature": "temperature",
  "OEE": "oee",
  "Gas efficiency": "gas-efficiency",
  "Distance driven": "distance-driven",
  "Latitude": "latitude",
  "Performance": "performance",
  "Run Time": "run-time",
  "Longitude": "longitude",
  "Avaliability": "avaliability",
  "Quality": "quality"
};

const AttributesComponent = () => {
  const dispatch = useDispatch();
  const editFleet = useSelector((state) => state.User.editFleet);
  const fleet1Attributes = useSelector((state) => state.User.fleet1Attributes);
  const fleet2Attributes = useSelector((state) => state.User.fleet2Attributes);
  const fleet3Attributes = useSelector((state) => state.User.fleet3Attributes);

  // Pick the correct fleet's attributes array
  const currentAttributes =
    editFleet === 1
      ? fleet1Attributes
      : editFleet === 2
      ? fleet2Attributes
      : fleet3Attributes;

  // Handler to update Redux when a checkbox is toggled
  const handleCheckboxChange = (attr) => {
    let newAttrs;
    
    if (currentAttributes.includes(attr)) {
      newAttrs = currentAttributes.filter((a) => a !== attr);
    } else {
      newAttrs = [...currentAttributes, attr];
    }
    if (editFleet === 1) dispatch(setFleet1Attributes(newAttrs));
    if (editFleet === 2) dispatch(setFleet2Attributes(newAttrs));
    if (editFleet === 3) dispatch(setFleet3Attributes(newAttrs));
  };

  return (
    <div className={styles.selectFleetContainer}>
      
      <Subtitle>Choose the telemetry to report</Subtitle>
      <br />
      <div className={styles.selectGrid}>
        {ALL_ATTRIBUTES.map((attr) => (
          <Checkbox
            key={attr}
            data-lgid={ATTR_KEY_MAP[attr]}
            label={attr}
            checked={currentAttributes.includes(attr)}
            onChange={() => handleCheckboxChange(attr)}
            // Optionally disable some checkboxes if needed:
            disabled={["Latitude", "Performance", "Run Time", "Longitude", "Avaliability", "Quality"].includes(attr)}
          />
        ))}
      </div>
    </div>
  );
};

export default AttributesComponent;