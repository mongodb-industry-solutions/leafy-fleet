import Card from '@leafygreen-ui/card';
import { H3,H2, Subtitle, Body } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import styles from './DetailsComponent.module.css';
import Icon from '@leafygreen-ui/icon';
import { Tabs, Tab } from '@leafygreen-ui/tabs';
import VehicleDataComponent from '../VehicleDataComponent/VehicleDataComponent.jsx';


const DetailsComponent = ({ car, onClose }) => {
  // Example: You can extend this with more data as needed
  const quickMetrics = [
    { label: "Fuel Level", value: `${car.fuel}%` },
    { label: "Mileage", value: `${car.mileage} km` },
    { label: "Efficiency", value: `${car.efficiency} km/l` },
    { label: "Alerts", value: car.alerts },
  ];

const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
        onClose();
    }
};

const getStatusBadgeClass = (status) => {
  switch (status) {
    case "Active":
      return `${styles.statusBadge} ${styles.statusActive}`;
    case "Maintenance":
      return `${styles.statusBadge} ${styles.statusMaintenance}`;
    case "Issue":
      return `${styles.statusBadge} ${styles.statusIssue}`;
    default:
      return `${styles.statusBadge} ${styles.statusDefault}`;
  }
};

return (
    <div className={styles.modalOverlay} onClick={handleOverlayClick}>
        <div className={styles.modalContent}>
            
            <button className={styles.closeButton} onClick={onClose}>×</button>
            <Card >
                <H3 darkMode={false}>{car.id} : {car.name}</H3>
                <div className={styles.UnderCar}>
                    <div className={getStatusBadgeClass(car.status)}>
  <Subtitle weight="medium">{car.status}</Subtitle>
</div>
                    <Body> {car.fleet}</Body>
                </div>
                
                <div className={styles.detailsGrid}>
                    {/* Left: Status & Quick Metrics */}
                    <div className={styles.leftSection}>
                        <div className={styles.status}> 

                            <div className={styles.IconSubtitle} >
                                <Icon glyph="Router"></Icon>
                                <Subtitle >Current Status</Subtitle>
                            </div>
                        <Body>Location: {car.location}</Body>
                        <Body>Driver: {car.driver}</Body>
                    </div>
                    <div className={styles.metricsBlock}>
                        <div className={styles.IconSubtitle}>
                            <Icon glyph="InfoWithCircle"></Icon>
                        <Subtitle > Quick Metrics</Subtitle>
                        </div>
                        <ul className={styles.metricsList}>
                            {quickMetrics.map((m) => (
                                <li key={m.label}>
                                    <span className={styles.metricLabel}>{m.label}: </span>
                                    <span className={styles.metricValue}>{m.value}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    </div>
                    {/* Right: Overview/Specs */}
                    <div className={styles.rightSection}>
                        <Tabs  aria-label="Details tabs">
                        <Tab name="Overview" default>
                            <div> {/*. separate div in 2 by width*/}</div>
                            <div> <VehicleDataComponent>{car}</VehicleDataComponent></div>



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
                            

                        </Tabs>

                                            </div>
                </div>
                <div className={styles.actions}>
                    <Button variant={Variant.Outline} size={Size.Default} onClick={onClose}>
                        Close
                    </Button>
                    
                </div>
            </Card>
        </div>
    </div>
);
};

export default DetailsComponent;