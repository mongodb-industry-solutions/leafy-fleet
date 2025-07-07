"use client"

import Card from '@leafygreen-ui/card';
import { H2, H3 , Subtitle, Body} from '@leafygreen-ui/typography';


import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import React from 'react';
import styles from './ResultsComponent.module.css';
import DetailsComponent from '../DetailsComponent/DetailsComponent.jsx';
import { useDispatch, useSelector } from 'react-redux';
import { setResults, setSelectedCar, setIsModalOpen } from '@/redux/slices/ResultSlice.js';


// On time, will replace this with real api call, use redux with setResults to populate the results
const cars = [
  {
    id: "FL001",
    name: "Ford Transit",
    fleet: "Delivery Fleet",
    status: "active",
    location: "Downtown",
    driver: "John Doe",
    fuel: 85,
    mileage: 45230,
    lastService: "2024-01-15",
    efficiency: 18.5,
    alerts: 0,
    coordinates: [-74.006, 40.7128],
    zone: "Zone A - Downtown",
    distance: 0.5, // km from search point
  },
  {
    id: "FL002",
    name: "Mercedes Sprinter",
    fleet: "Delivery Fleet",
    status: "maintenance",
    location: "Garage A",
    driver: "Unassigned",
    fuel: 20,
    mileage: 67890,
    lastService: "2024-01-10",
    efficiency: 16.2,
    alerts: 2,
    coordinates: [-74.01, 40.72],
    zone: "Zone B - Industrial",
    distance: 1.2,
  },
  {
    id: "EX001",
    name: "BMW 7 Series",
    fleet: "Executive Fleet",
    status: "active",
    location: "Airport",
    driver: "Mike Johnson",
    fuel: 65,
    mileage: 23450,
    lastService: "2024-01-20",
    efficiency: 22.1,
    alerts: 0,
    coordinates: [-73.7781, 40.6413],
    zone: "Zone C - Airport",
    distance: 15.3,
  },
  {
    id: "EX002",
    name: "Audi A8",
    fleet: "Executive Fleet",
    status: "active",
    location: "City Center",
    driver: "Sarah Wilson",
    fuel: 90,
    mileage: 18900,
    lastService: "2024-01-18",
    efficiency: 21.8,
    alerts: 0,
    coordinates: [-74.0059, 40.7589],
    zone: "Zone A - Downtown",
    distance: 2.1,
  },
  {
    id: "SV002",
    name: "Ford F-150",
    fleet: "Service Fleet",
    status: "active",
    location: "Warehouse B",
    driver: "Lisa Davis",
    fuel: 75,
    mileage: 56780,
    lastService: "2024-01-12",
    efficiency: 15.8,
    alerts: 1,
    coordinates: [-74.209, 40.7505],
    zone: "Zone D - Warehouse",
    distance: 8.7,
  },
]


const ResultsComponent = ( ) => {

    
    const dispatch = useDispatch();
    const results = useSelector((state) => state.Result.results);
    const selectedCar = useSelector((state) => state.Result.selectedCar);
    const isModalOpen = useSelector((state) => state.Result.isModalOpen);



    const getStatusIcon = (status) => {
  switch (status) {
    case "active":
      return <span className={`${styles.statusCircle} ${styles.statusActive}`} />;
    case "maintenance":
      return <span className={`${styles.statusCircle} ${styles.statusMaintenance}`} />;
    case "issue":
      return <span className={`${styles.statusCircle} ${styles.statusIssue}`} />;
    default:
      return <span className={`${styles.statusCircle} ${styles.statusDefault}`} />;
  }
};

  const handleCarClick = (car) => {
    dispatch(setSelectedCar({ car }));
    dispatch(setIsModalOpen({ isModalOpen: true }));
  }

  const handleCloseModal = () => {
    dispatch(setIsModalOpen({ isModalOpen: false }));
    dispatch(setSelectedCar({ car: null }));
  }
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleCloseModal();
    }
  };
  return (
    <Card className="card-styles" as="article">
    <div className={styles.resultsCard}> 
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'left' ,  }}>
            <H3 >Search Results </H3>
        </div>

        <div className={styles.resultsContainer}>
        {cars.slice(0, 10).map((car, index) => (
            <div key={car.id}>
            <div
                className={styles.row}
                tabIndex={0}
            >
                <div className={styles.grid}>
                <div className={styles.statusAndId}>
                    {getStatusIcon(car.status)}
                    <Subtitle className={styles.carId}>{car.id}</Subtitle>
                </div>
                <div>
                    <Body>{car.driver}</Body>
                    <p className={styles.fleet}>{car.fleet}</p>
                </div>
                
                {car.distance !== null && (
                    <div className={styles.distanceBlock}>
                    <p className={styles.distance}>{car.distance} km</p>
                    <p className={styles.distanceLabel}>Distance</p>
                    </div>
                )}
                <div className={styles.buttonBlock}>
                    <Button size={Size.Small} variant={Variant.Outline} onClick={e => { e.stopPropagation(); handleCarClick(car); }}>
                    View Details
                    </Button>
                </div>
                </div>
            </div>
            {index < cars.length - 1 && <div className={styles.separator} />}
            </div>
        ))}
        </div>
                    
    </div>  

    {isModalOpen && (
        <div className={styles.modalOverlay} onClick={handleOverlayClick}>
          
            <DetailsComponent car={selectedCar} onClose={handleCloseModal}/>
          
        </div>
      )}

    </Card>
  );
}
export default ResultsComponent;