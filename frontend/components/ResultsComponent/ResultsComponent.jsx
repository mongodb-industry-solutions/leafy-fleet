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
import { Spinner } from '@leafygreen-ui/loading-indicator'; //cuando haga llamada a api

// On time, will replace this with real api call, use redux with setResults to populate the results


const ResultsComponent = ( ) => {

    
    const dispatch = useDispatch();
    const results = useSelector((state) => state.Result.results);
    const selectedCar = useSelector((state) => state.Result.selectedCar);
    const isModalOpen = useSelector((state) => state.Result.isModalOpen);



    const getStatusIcon = (status) => {
  switch (status) {
    case "Active":
      return <span className={`${styles.statusCircle} ${styles.statusActive}`} />;
    case "Maintenance":
      return <span className={`${styles.statusCircle} ${styles.statusMaintenance}`} />;
    case "Issue":
      return <span className={`${styles.statusCircle} ${styles.statusIssue}`} />;
    default:
      return <span className={`${styles.statusCircle} ${styles.statusDefault}`} />;
  }
};

  const handleCarClick = (car) => {
    dispatch(setSelectedCar({ car }));
    console.log("Selected car:", car);
    dispatch(setIsModalOpen({ isModalOpen: true }));
  }

  const handleCloseModal = () => {
    dispatch(setIsModalOpen({ isModalOpen: false }));
    dispatch(setSelectedCar({ car: null }));
  }
  
  return (
    <Card className="card-styles" as="article">
      <div className={styles.resultsCard}> 
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'left' }}>
          <H3>Search Results</H3>
        </div>
        <div className={styles.resultsContainer}>
          {results && results.length > 0 ? (
            results.slice(0, 10).map((car, index) => (
              <div key={car.car_id}>
                <div className={styles.row} tabIndex={0}>
                  <div className={styles.grid}>
                    <div className={styles.statusAndId}>
                      {getStatusIcon(car.status)}
                      <Subtitle className={styles.carId}> Car ID: {car.car_id}</Subtitle>
                    </div>
                    <div>
                      <Body>Satus: {car.status}</Body>
                      <p className={styles.fleet}>{car.fleet}</p>
                    </div>
                    {car.distance !== null && (
                      <div className={styles.distanceBlock}>
                        <p className={styles.distance}>{car.distance} km</p>
                        <p className={styles.distanceLabel}>Distance</p>
                      </div>
                    )}
                    {car.distance === null && (
                      <div className={styles.distanceBlock}>
                        <p className={styles.distance}>{car.current_geozone}</p>
                        <p className={styles.distanceLabel}>Current Geofence</p>
                      </div>
                      )}
                    <div className={styles.buttonBlock}>
                      <Button 
                        size={Size.Small} 
                        variant={Variant.Outline} 
                        onClick={e => { 
                          e.stopPropagation(); 
                          handleCarClick(car); 
                        }}
                      >
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
                {index < results.length - 1 && <div className={styles.separator} />}
              </div>
            ))
          ) : (
            <div className={styles.noResults}>
              <Body>No vehicles found matching your search criteria</Body>
            </div>
          )}
        </div>

        {isModalOpen && <DetailsComponent onClose={handleCloseModal} />}
      </div>
    </Card>
  );
};

export default ResultsComponent;