import {Code, Panel} from '@leafygreen-ui/code';
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import styles from './CodeComponent.module.css'; // Adjust the path as necessary


const zones = {
    "zone1": [
        { lat: 30.2900, lon: -97.7500 },
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.3100, lon: -97.7300 },
        { lat: 30.3100, lon: -97.7500 },
    ],
    "zone2": [
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7100 },
        { lat: 30.3100, lon: -97.7100 },
        { lat: 30.3100, lon: -97.7300 },
    ],
    "zone3": [
        { lat: 30.2700, lon: -97.7500 },
        { lat: 30.2700, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7300 },
        { lat: 30.2900, lon: -97.7500 },
    ],
    "zone4": [
        { lat: 30.2700, lon: -97.7300 },
        { lat: 30.2700, lon: -97.7100 },
        { lat: 30.2900, lon: -97.7100 },
        { lat: 30.2900, lon: -97.7300 },
    ],
};

function getZoneCenter(points) {
  const sum = points.reduce(
    (acc, point) => {
      acc.lat += point.lat;
      acc.lon += point.lon;
      return acc;
    },
    { lat: 0, lon: 0 }
  );

  const count = points.length;
  return {
    lat: sum.lat / count,
    lon: sum.lon / count,
  };
}


const CodeComponent = () => {
    const dispatch = useDispatch();
    const selectedType = useSelector(state => state.Overview.type);
    const fleetsFilter = useSelector(state => state.Overview.fleetsFilter);
    const geoFences = useSelector(state => state.Overview.geoFences);
    const location = useSelector(state => state.Overview.location);
    const maxDist = useSelector(state => state.Overview.maxDistance);
    const minDist = useSelector(state => state.Overview.minDistance);


 const generateDynamicQuery = () => {
  if (selectedType === "nearest") {
    const zonePoints = zones[location];
    if (!zonePoints) {
      return `db.vehicles.find({
  location: {
    $nearSphere: {
      $geometry: {
        type: "Point",
        coordinates: [ , ]
      }${minDist ? `,
      $minDistance: ${minDist}` : ""}${maxDist ? `,
      $maxDistance: ${maxDist}` : ""}
    }
  }
})`;
    }
    const coordinates = getZoneCenter(zonePoints);
    return `db.vehicles.find({
  location: {
    $nearSphere: {
      $geometry: {
        type: "Point",
        coordinates: [${coordinates.lon}, ${coordinates.lat}]
      }${minDist ? `,
      $minDistance: ${minDist}` : ""}${maxDist ? `,
      $maxDistance: ${maxDist}` : ""}
    }
  }
})`;
  } else if (selectedType === "inside") {
    const selectedZones = Array.isArray(geoFences) ? geoFences : [];
    if (selectedZones.length === 0) {
      // No zones selected, empty polygon
      return `db.vehicles.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: []
      }
    }
  }
})`;
    } else if (selectedZones.length === 1) {
      // Single zone, use Polygon
      const zoneCoords = zones[selectedZones[0]] || [];
      const formatted = zoneCoords.map(p => [p.lon, p.lat]);
      if (
        formatted.length &&
        (formatted[0][0] !== formatted.at(-1)[0] ||
          formatted[0][1] !== formatted.at(-1)[1])
      ) {
        formatted.push(formatted[0]);
      }
      return `db.vehicles.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: ${JSON.stringify([formatted], null, 2)}
      }
    }
  }
})`;
    } else {
      // Multiple zones, use MultiPolygon
      const multiPolygonCoordinates = selectedZones.map(zoneName => {
        const zoneCoords = zones[zoneName] || [];
        const formatted = zoneCoords.map(p => [p.lon, p.lat]);
        if (
          formatted.length &&
          (formatted[0][0] !== formatted.at(-1)[0] ||
            formatted[0][1] !== formatted.at(-1)[1])
        ) {
          formatted.push(formatted[0]);
        }
        return [formatted];
      });
      return `db.vehicles.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "MultiPolygon",
        coordinates: ${JSON.stringify(multiPolygonCoordinates, null, 2)}
      }
    }
  }
})`;
    }
  }
};

    return (
        <div className={styles.CodeContainer}>
    <Code
    label="MongoDB Query Example"
      language="javascript"
      showLineNumbers={true}
      onCopy={() => {}}
      darkMode={true}
    >
      {generateDynamicQuery()}
    </Code>
  </div>
    );
};
export default CodeComponent;