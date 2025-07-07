import Card from '@leafygreen-ui/card';
import { H2, H3 , Subtitle, Body} from '@leafygreen-ui/typography';


import Button, { Variant, Size } from '@leafygreen-ui/button';
import styles from './DetailsComponent.module.css';

const DetailsComponent = ({ car }) => {

    return(
    <Card className={styles.resultsCard} >
        <div className={styles.resultsHeader}>
            <H3>Vehicle Details</H3>
        </div>
        <div className={styles.detailsContainer}>
            <Subtitle>Vehicle ID: {car.id}</Subtitle>
            <Body>Name: {car.name}</Body>
            <Body>Fleet: {car.fleet}</Body>
            <Body>Status: {car.status}</Body>
            <Body>Location: {car.location}</Body>
            <Body>Driver: {car.driver}</Body>
            <Body>Fuel Level: {car.fuel}%</Body>
            <Body>Mileage: {car.mileage} km</Body>
            <Body>Last Service: {new Date(car.lastService).toLocaleDateString()}</Body>
            <Body>Efficiency: {car.efficiency} km/l</Body>
            <Body>Alerts: {car.alerts}</Body>
            <Button
                variant={Variant.Primary}
                size={Size.Default}
                onClick={() => alert(`More details for ${car.name}`)}
            >
                View More
            </Button>
        </div>
    </Card>
    );

}

export default DetailsComponent;