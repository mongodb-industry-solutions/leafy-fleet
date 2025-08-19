"use client";
import { H1, H2, Subtitle, Body, InlineCode, InlineKeyCode, Disclaimer, Overline, Link, BackLink } from '@leafygreen-ui/typography';
import styles from './InforcardComponent.module.css';

// Fleet info card





const InfocardComponent = ({ title, car, fleetSize }) => {

    

    const activeCars = car.filter(
        (car) => !car.isCrashed && car.is_engine_running && !car.isMoving
    );

    return (

        <div className={styles.container}>
            <div className={styles.topPart} style={{ flex: 1 }}>
                <Subtitle>{title}</Subtitle>
                <div className={styles.pill}>
                    <Body>{fleetSize} Vehicles</Body>
                </div>
            </div>
            <div className={styles.bottomPart} style={{ flex: 5 }}>
                <div className={styles.statusIndicator}>
                    <Body style={{ color: '#17A34A' }}>{activeCars.length}</Body>
                    <Body style={{ color: '#4B5563' }} baseFontSize={16}>Active</Body>
                </div>
                <div className={styles.issueIndicator}>
                    <Body style={{ color: '#DC2625' }}>{car.length - activeCars.length}</Body>
                    <Body style={{ color: '#4B5563' }} baseFontSize={16}>Issues</Body>
                </div>
            </div>
        </div>
    );
}

module.exports = InfocardComponent;