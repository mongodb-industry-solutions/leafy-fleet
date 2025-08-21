import { Tabs, Tab } from '@leafygreen-ui/tabs';    
import VehicleDataComponent from '../VehicleDataComponent/VehicleDataComponent.jsx';    
import { H3, Body, Subtitle } from '@leafygreen-ui/typography';    
import { useSelector } from 'react-redux';    
import styles from './TabsComponent.module.css';    
import StaticComponent from '../StaticComponent/StaticComponent.jsx';
    
const TabsComponent = () => {    
  const car = useSelector((state) => state.Result.selectedCar);   
  const staticCar = useSelector((state) => state.Result.staticSelectedCar); 
    
  // Add comprehensive null checks  
  if (!car || Object.keys(car).length === 0 || !staticCar) {  
    return <div>Loading car data...</div>;  
  }  
  
  // Log to debug what we're actually getting  
  console.log("TabsComponent car data:", car);  
  
  return (    
    <Tabs aria-label="Details tabs">    
      <Tab name="Overview" default>    
        <div className={styles.HorizontalCutHalf}>     
          <div className={styles.VerticalCutHalf}>    
            <div className={styles.topHalf}>     
              <Subtitle>Performance</Subtitle>
              <Body weight='medium'>Quality Score: {car.quality_score ? (car.quality_score * 100).toFixed(1) : 'N/A'}%</Body>  
              <Body weight='medium'>Availability Score: {car.availability_score ? (car.availability_score * 100).toFixed(1) : 'N/A'}%</Body>  
              <Body weight='medium'>Performance Score: {car.performance_score ? (car.performance_score * 100).toFixed(1) : 'N/A'}%</Body>
            </div>    
            <div className={styles.topHalf}>    
              <Subtitle>Usage</Subtitle>   
              <Body weight='medium'>Traveled Distance: {car.traveled_distance ? car.traveled_distance.toFixed(2) : 'N/A'} km</Body>  
              <Body weight='medium'>Average Speed: {car.average_speed || 'N/A'} km/h</Body>  
              <Body weight='medium'>Engine Oil Level: {car.engine_oil_level || 'N/A'} L</Body>  
            </div>    
          </div>    
          <div className={styles.bottomHalf}>     
            <Subtitle>Vehicle Document Model</Subtitle>     
            <br />    
            <VehicleDataComponent/>  
          </div>    
        </div>    
      </Tab>    
          
      <Tab name="Specs">  
        <div className={styles.bottomHalf}>     
            <Subtitle>Vehicle Static Model</Subtitle>     
            <br />    
            <StaticComponent/>  
          </div>     
        
      </Tab>    
    </Tabs>  
  );    
};    
    
export default TabsComponent;  
