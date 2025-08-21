import Code from "@leafygreen-ui/code";    
import { useSelector } from "react-redux";    
import styles from './VehicleDataComponent.module.css'  
import { ATTR_KEY_MAP } from '../AttributesComponent/AttributesComponent'; // Import the mapping  
  
const VehicleDataComponent = () => {  
    // Using redux for car instead of props    
    const car = useSelector((state) => state.Result.selectedCar);  
    const fleet1Attributes = useSelector(state => state.User.fleet1Attributes);  
    const fleet2Attributes = useSelector(state => state.User.fleet2Attributes);  
    const fleet3Attributes = useSelector(state => state.User.fleet3Attributes);  
      
    // Helper function to get fleet number based on car_id  
    const getFleetNumber = (carId) => {  
        if (carId >= 1 && carId <= 100) {  
            return 1;  
        } else if (carId >= 101 && carId <= 200) {  
            return 2;  
        } else if (carId >= 201 && carId <= 300) {  
            return 3;  
        } else {  
            return Math.floor(carId/100) + 1;  
        }  
    };  
  
    // Helper function to get fleet attributes  
    const getFleetAttributes = (fleetNumber) => {  
        switch (fleetNumber) {  
            case 1: return fleet1Attributes;  
            case 2: return fleet2Attributes;  
            case 3: return fleet3Attributes;  
            default: return null;  
        }  
    };  
  
    // Filter car data based on fleet attributes  
    const getFilteredCarData = () => {  
        if (!car) return {};  
          
        // Remove distance fields first  
        const { distance, distance_to_geofence, ...carWithoutDistance } = car;  
          
        // Get fleet attributes  
        const fleetNumber = getFleetNumber(car.car_id);  
        const fleetAttributes = getFleetAttributes(fleetNumber);  
          
        // If no fleet attributes defined, return all data  
        if (!fleetAttributes || fleetAttributes.length === 0) {  
            return carWithoutDistance;  
        }  
          
        // Convert display names to database field names  
        const allowedDbFields = fleetAttributes.map(attr => ATTR_KEY_MAP[attr] || attr);  
          
        // Always include essential fields  
        const filtered = {  
            car_id: carWithoutDistance.car_id,  
            _id: carWithoutDistance._id,  
            timestamp: carWithoutDistance.timestamp  
        };  
          
        // Add computed fields if they exist  
        if (carWithoutDistance.status) filtered.status = carWithoutDistance.status;  
        if (carWithoutDistance.fleet) filtered.fleet = carWithoutDistance.fleet;  
          
        // Add allowed fleet-specific attributes  
        allowedDbFields.forEach(field => {  
            if (carWithoutDistance.hasOwnProperty(field) && !filtered.hasOwnProperty(field)) {  
                filtered[field] = carWithoutDistance[field];  
            }  
        });  
          
        return filtered;  
    };  
  
    const filteredCarData = getFilteredCarData();  
      
    return (      
        <div className={styles.CodeCont}>      
            <Code language="json" onCopy={() => {}}>      
                {JSON.stringify(filteredCarData, null, 2)}      
            </Code>      
        </div>      
    );      
};    
  
export default VehicleDataComponent;  
