import {Code, Panel} from '@leafygreen-ui/code';
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import styles from './CodeComponent.module.css'; // Adjust the path as necessary
import { geofenceCoordinates, getGeofenceByName } from '@/components/Geofences/geofences'; // Import the geofence data  



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
            const selectedGeofence = getGeofenceByName(location);  
            if (!selectedGeofence) {  
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
              
            const [lon, lat] = selectedGeofence.centroid.coordinates;  
            return `db.vehicles.find({  
  location: {  
    $nearSphere: {  
      $geometry: {  
        type: "Point",  
        coordinates: [${lon}, ${lat}]  
      }${minDist ? `,  
      $minDistance: ${minDist}` : ""}${maxDist ? `,  
      $maxDistance: ${maxDist}` : ""}  
    }  
  }  
})`;  
        } else if (selectedType === "inside") {  
            const selectedZones = Array.isArray(geoFences) ? geoFences : [];  
            if (selectedZones.length === 0) {  
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
                const selectedGeofence = getGeofenceByName(selectedZones[0]);  
                if (!selectedGeofence) return "// No valid geofence selected";  
                  
                return `db.vehicles.find({  
  location: {  
    $geoWithin: {  
      $geometry: {  
        type: "Polygon",  
        coordinates: ${JSON.stringify(selectedGeofence.geometry.coordinates, null, 2)}  
      }  
    }  
  }  
})`;  
            } else {  
                // Multiple zones, use $or with multiple queries  
                const multiQueryArray = selectedZones.map(zoneName => {  
                    const selectedGeofence = getGeofenceByName(zoneName);  
                    if (!selectedGeofence) return null;  
                      
                    return `{  
    location: {  
      $geoWithin: {  
        $geometry: {  
          type: "Polygon",  
          coordinates: ${JSON.stringify(selectedGeofence.geometry.coordinates, null, 2)}  
        }  
      }  
    }  
  }`;  
                }).filter(Boolean);  
                  
                return `db.vehicles.find({  
  $or: [  
    ${multiQueryArray.join(',\n    ')}  
  ]  
})`;  
            }  
        }  
    };  
  
    return (  
        <div className={styles.CodeContainer} style={{ maxHeight: '400px', overflow: 'auto' }}>  
            <Code  
                label="MongoDB Query Example"  
                language="javascript"  
                showLineNumbers={true}  
                onCopy={() => {}}  
                darkMode={true}  
                expandable={false}  
            >  
                {generateDynamicQuery()}  
            </Code>  
        </div>  
    );  
};  

export default CodeComponent;