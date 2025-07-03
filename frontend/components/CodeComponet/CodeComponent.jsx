import {Code, Panel} from '@leafygreen-ui/code';
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import styles from './CodeComponent.module.css'; // Adjust the path as necessary


const codeSnippet = `
function greeting(entity) {
  return \`Hello, \${entity}!\`;
}


console.log(greeting('World'));
`;


// esto no estara aqui, se sacara prob de collection de geofences :)
const zones = {
    "Zone 1": [
        { lat: 30.2900, lon: -97.7500 },
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.3100, lon: -97.7300 },
        { lat: 30.3100, lon: -97.7500 },
    ],
    "Zone 2": [
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7100 },
        { lat: 30.3100, lon: -97.7100 },
        { lat: 30.3100, lon: -97.7300 },
    ],
    "Zone 3": [
        { lat: 30.2700, lon: -97.7500 },
        { lat: 30.2700, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7500 },
    ],
    "Zone 4": [
        { lat: 30.2700, lon: -97.7300 },
        { lat: 30.2700, lon: -97.7100 },
        { lat: 30.2900, lon: -97.7100 },
        { lat: 30.2900, lon: -97.7300 },
    ],
};

const CodeComponent = () => {
    const dispatch = useDispatch();
    const selectedType = useSelector(state => state.Overview.type);
    const fleetsFilter = useSelector(state => state.Overview.fleetsFilter);
    const geoFences = useSelector(state => state.Overview.geoFences);
/*
    const generateDynamicQuery = () => {
    
   
        //get from redux the value of OverviewSlice

    switch (selectedType) {
      case "nearest":
        //get from redux

        return `db.vehicles.find({
                    location: {
                        $nearSphere: {
                            $geometry: {
                                type: "Point",
                                coordinates: [${coordinates[0]}, ${coordinates[1]}]
                                }${
                                    minDist
                                ? `,
                                $minDistance: ${minDist}`
                                : ""
                                }${
                                maxDist
                                ? `,
                                $maxDistance: ${maxDist}`
                                : ""
                                }
                            }
                        }
                })`
      default:
        return `db.vehicles.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-74.0200, 40.7000],
          [-74.0000, 40.7000],
          [-74.0000, 40.7300],
          [-74.0200, 40.7300],
          [-74.0200, 40.7000]
        ]]
      }
    }
  }
})`,
} }
*/
  


    return (
        <div className={styles.CodeContainer}>
    <Code
    label="MongoDB Query Example"
      language="javascript"
      showLineNumbers={true}
      onCopy={() => {}}
      darkMode={true}
    >
      {codeSnippet}
    </Code>
  </div>
    );
};
export default CodeComponent;