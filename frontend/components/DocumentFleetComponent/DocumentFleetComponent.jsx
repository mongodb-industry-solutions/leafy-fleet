import styles from "./DocumentFleetComponent.module.css";
import Code from "@leafygreen-ui/code";
import { Subtitle } from "@leafygreen-ui/typography";
import { useSelector } from "react-redux";

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
  "Quality": "quality",
  "Current Geozone": "current-geozone",
  "Coordinates": "coordinates", 
  "Speed": "speed",
};

const DocumentFleetComponent = () => {
  const editFleet = useSelector((state) => state.User.editFleet);
  const fleet1Attributes = useSelector((state) => state.User.fleet1Attributes);
  const fleet2Attributes = useSelector((state) => state.User.fleet2Attributes);
  const fleet3Attributes = useSelector((state) => state.User.fleet3Attributes);
  const fleet1Name = useSelector((state) => state.User.fleet1Name);
  const fleet2Name = useSelector((state) => state.User.fleet2Name);
  const fleet3Name = useSelector((state) => state.User.fleet3Name);
  const fleet1Capacity = useSelector((state) => state.User.fleet1Capacity);
  const fleet2Capacity = useSelector((state) => state.User.fleet2Capacity);
  const fleet3Capacity = useSelector((state) => state.User.fleet3Capacity);
  const selectedFleets = useSelector((state) => state.User.selectedFleets)
  const allFleetData = [
    {
        name: fleet1Name,
        size: fleet1Capacity,
        attributes: fleet1Attributes.map(attr => ATTR_KEY_MAP[attr] || attr),
    },
    {
        name: fleet2Name,
        size: fleet2Capacity,
        attributes: fleet2Attributes.map(attr => ATTR_KEY_MAP[attr] || attr),
    },
    {
        name: fleet3Name,
        size: fleet3Capacity,
        attributes: fleet3Attributes.map(attr => ATTR_KEY_MAP[attr] || attr),
    },
    ];

    const fleets = allFleetData.slice(0, selectedFleets);


// Create example object of this session, should show default only selected fleets (can be 1,2 or 3)
  const exampleJSON = {
    _id: "ObjectId('64f8c1e2d4f3a5b6c7d8e9f0')",
    thread_id: "thread_",
    fleets,
    createdOn: new Date().toISOString(),
    lastUsed: new Date().toISOString(),
  };


  return (
    <div>
        <div className={styles.centerSub}>  <Subtitle>  Document model of fleets</Subtitle> </div>
       
        <div className={styles.Code}> 
            <Code language="json">
                {JSON.stringify(exampleJSON, null, 2)
                .replace(/"ObjectId\((.*?)\)"/g, "ObjectId($1)") // Optional formatting
                }
            </Code>
        </div>
    </div>
  );
};

export default DocumentFleetComponent;
