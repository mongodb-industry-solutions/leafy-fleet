import { Tabs, Tab } from '@leafygreen-ui/tabs';
import VehicleDataComponent from '../VehicleDataComponent/VehicleDataComponent.jsx';
import { H3, Body, Subtitle } from '@leafygreen-ui/typography';
import { useSelector } from 'react-redux';
import styles from './TabsComponent.module.css';

const TabsComponent = () => {
const car = useSelector((state) => state.Result.selectedCar);

return (
    <Tabs  aria-label="Details tabs">
        <Tab name="Overview" default>
            <div className={styles.HorizontalCutHalf}> 
            <div className={styles.VerticalCutHalf}>
                <div className={styles.topHalf}> 
                    <Subtitle >Performance</Subtitle> <br />
                    <Body weight='medium'> OEE: {car.efficiency*9}</Body>
                </div>
                <div className={styles.topHalf}>
                    <Subtitle >Usage</Subtitle> <br />
                    <Body weight='medium'> Distance current trip: {car.distance*20} miles</Body>
                    <Body weight='medium'> Oil level: {car.fuel-13} %</Body>
                </div>

            </div>
            <div className={styles.bottomHalf}> 
                <Subtitle >Vehicle Document Model</Subtitle> 
                <br />
                <VehicleDataComponent/></div>
            </div>
          
        </Tab>
        
        <Tab name="Specs">
                            
            <H3>Specs</H3>
            <br />
            <Body weight='medium'> Make and Model</Body>
            <Subtitle>{car.year} {car.name}</Subtitle>
            <br />
            <Body weight='medium'> Fleet</Body>
            <Subtitle>{car.fleet}</Subtitle>
            <br />
            <Body weight='medium'> Licence Plate</Body>
            <Subtitle>{car.licencePlate}</Subtitle> 
        </Tab>
    </Tabs>)

};

export default TabsComponent;