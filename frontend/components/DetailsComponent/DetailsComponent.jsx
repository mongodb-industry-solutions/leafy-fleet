import Card from '@leafygreen-ui/card';
import { H3,H2, Subtitle, Body } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import styles from './DetailsComponent.module.css';
import Icon from '@leafygreen-ui/icon';
import TabsComponent from '../TabsComponent/TabsComponent';
import { useSelector, useDispatch } from 'react-redux';
import { setIsModalOpen, setSelectedCar } from '../../redux/slices/ResultSlice';
const DetailsComponent = () => {
    const dispatch = useDispatch();
    const car = useSelector((state) => state.Result.selectedCar);
  // Example: You can extend this with more data as needed
    const quickMetrics = [
    { label: "Fuel Level", value: `${car.fuel}%` },
    { label: "Mileage", value: `${car.mileage} km` },
    { label: "Efficiency", value: `${car.efficiency} km/l` },
    { label: "Alerts", value: car.alerts },
    ];

    const handleClose = () => {
        dispatch(setIsModalOpen({ isModalOpen: false }));
        dispatch(setSelectedCar({ car: null }));
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
    <div className={styles.modalOverlay} onClick={e => { if (e.target === e.currentTarget) handleClose(); }}>
        <div className={styles.modalContent}>
            
            <button className={styles.closeButton} onClick={handleClose}>×</button>
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
                        
                        <TabsComponent />
                    </div>
                </div>
                <div className={styles.actions}>
                    <Button variant={Variant.Outline} size={Size.Default} onClick={handleClose}>
                        Close
                    </Button>
                    
                </div>
            </Card>
        </div>
    </div>
);
};

export default DetailsComponent;