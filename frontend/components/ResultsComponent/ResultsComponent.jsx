"use client"

import Card from '@leafygreen-ui/card';
import { H2, H3 , Subtitle, Body} from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import React from 'react';
import styles from './ResultsComponent.module.css';
import DetailsComponent from '../DetailsComponent/DetailsComponent.jsx';
import { useDispatch, useSelector } from 'react-redux';
import { setResults, setSelectedCar, setIsModalOpen, setStaticSelectedCar } from '@/redux/slices/ResultSlice.js';
import {setIsLoading} from '@/redux/slices/OverviewSlice.js';
import { Spinner } from '@leafygreen-ui/loading-indicator'; //cuando haga llamada a api
// On time, will replace this with real api call, use redux with setResults to populate the results


const ResultsComponent = ( ) => {

    
    const dispatch = useDispatch();
    const results = useSelector((state) => state.Result.results);
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

  // call 
  // FIXED: Now returns the data and handles URL properly  
  const handleSearchStatic = async (id) => {    
    try {    
      setIsLoading(true);  
        
      // Handle URL properly - don't double-add protocol  
      let baseUrl = process.env.NEXT_PUBLIC_STATIC_SERVICE_URL;  
        
      // Only add http:// if no protocol exists  
      if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {  
        baseUrl = `http://${baseUrl}`;  
      }  
      const response = await fetch(`${baseUrl}/static/${id}`);    
        
      if (!response.ok) {    
        throw new Error(`HTTP error! Status: ${response.status}`);    
      }    
        
      const data = await response.json();    
      console.log('Static data fetched:', data);  
        
      // Store in Redux  
      dispatch(setStaticSelectedCar({ staticCar: data }));  
        
      // IMPORTANT: Return the data so it can be used in handleCarClick  
      return data;  
        
    } catch (error) {    
      console.error('Error fetching static car data:', error);    
      return null; // Return null on error  
    } finally {  
      setIsLoading(false);  
    }  
  };  

  const handleCarClick = async (car) => {    
    dispatch(setSelectedCar({ car }));
    //check this logic
    try {
      const staticData = await handleSearchStatic(car.car_id);    
        
      if (staticData) {  
        console.log("Static car data:", staticData);  
        // Open modal only after successfully fetching static data  
        dispatch(setIsModalOpen({ isModalOpen: true }));  
        dispatch(setStaticSelectedCar({ car: staticData }));
      } else {  
        // Handle error case - maybe show error message or open modal anyway  
        dispatch(setIsModalOpen({ isModalOpen: true }));  
      }  
    } catch (error) {
      console.error("Error fetching static data:", error);
    }
    console.log("Selected car:", car);
    dispatch(setIsModalOpen({ isModalOpen: true }));
  }

  const handleCloseModal = () => {
    dispatch(setIsModalOpen({ isModalOpen: false }));
    dispatch(setSelectedCar({ car: null }));
  }
    const isSearchLoading = useSelector((state) => state.Overview.isLoading);  

  
  return (
    <Card className="card-styles" as="article">
      <div className={styles.resultsCard}> 
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'left' }}>
          <H3>Search Results</H3>
         {isSearchLoading && <Spinner  />}  

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