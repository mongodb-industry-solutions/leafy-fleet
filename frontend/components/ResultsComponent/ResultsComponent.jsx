"use client";  
  
import Card from '@leafygreen-ui/card';  
import { H2, H3, Subtitle, Body } from '@leafygreen-ui/typography';  
import Button, { Variant, Size } from '@leafygreen-ui/button';  
import Icon from '@leafygreen-ui/icon';  
import React, { useEffect, useState, useCallback } from 'react';  
import styles from './ResultsComponent.module.css';  
import DetailsComponent from '../DetailsComponent/DetailsComponent.jsx';  
import { useDispatch, useSelector } from 'react-redux';  
import { setResults, setSelectedCar, setIsModalOpen, setStaticSelectedCar } from '@/redux/slices/ResultSlice.js';  
import { setIsLoading } from '@/redux/slices/OverviewSlice.js';  
import { Spinner } from '@leafygreen-ui/loading-indicator';  
  
const ResultsComponent = () => {  
    // Track if this is the first time on the page (no searches performed yet)      
    const [hasPerformedSearch, setHasPerformedSearch] = useState(false);  
      
    const dispatch = useDispatch();  
    const results = useSelector((state) => state.Result.results);  
    const isModalOpen = useSelector((state) => state.Result.isModalOpen);  
    const isSearchLoading = useSelector((state) => state.Overview.isLoading);  
  
    // Track when search starts to clear results and set search flag  
    useEffect(() => {  
        if (isSearchLoading) {  
            setHasPerformedSearch(true);  
            // Clear results when starting a new search  
            dispatch(setResults(null));  
        }  
    }, [isSearchLoading, dispatch]);  
  
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
  
    // Handle fetching static car data (separate loading state)  
    const handleSearchStatic = useCallback(async (id) => {  
        try {  
            let baseUrl = process.env.NEXT_PUBLIC_STATIC_SERVICE_URL;  
  
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
            return data;  
  
        } catch (error) {  
            console.error('Error fetching static car data:', error);  
            return null;  
        }  
    }, [dispatch]);  
  
    const handleCarClick = useCallback(async (car) => {  
        dispatch(setSelectedCar({ car }));  
        console.log("Selected car:", car);  
  
        try {  
            const staticData = await handleSearchStatic(car.car_id);  
  
            if (staticData) {  
                console.log("Static car data:", staticData);  
            }  
  
            // Always open modal regardless of static data success/failure  
            dispatch(setIsModalOpen({ isModalOpen: true }));  
  
        } catch (error) {  
            console.error("Error fetching static data:", error);  
            // Still open modal even on error  
            dispatch(setIsModalOpen({ isModalOpen: true }));  
        }  
    }, [dispatch, handleSearchStatic]);  
  
    const handleCloseModal = useCallback(() => {  
        dispatch(setIsModalOpen({ isModalOpen: false }));  
        dispatch(setSelectedCar({ car: null }));  
        dispatch(setStaticSelectedCar({ staticCar: null }));  
    }, [dispatch]);  
  
    // Determine what to render based on state  
    const renderContent = () => {  
        // State 2: First time on page (no search performed yet)  
        if (results === null && !isSearchLoading && !hasPerformedSearch) {  
            return (  
                <div className={styles.welcomeState}>  
                  
                    <Body>Use the search above to find vehicles in your fleet</Body>  
                </div>  
            );  
        }  
  
        // State 3: Search completed but no results (empty array)  
        if (Array.isArray(results) && results.length === 0) {  
            return (  
                <div className={styles.noResults}>  
                    <Body>No vehicles found matching your search criteria</Body>  
                    <Subtitle>Try adjusting your search parameters</Subtitle>  
                </div>  
            );  
        }  
  
        // State 4: Results found  
        if (Array.isArray(results) && results.length > 0) {  
            return (  
                <>  
                    {results.slice(0, 10).map((car, index) => (  
                        <div key={car.car_id}>  
                            <div className={styles.row} tabIndex={0}>  
                                <div className={styles.grid}>  
                                    <div className={styles.statusAndId}>  
                                        {getStatusIcon(car.status)}  
                                        <Subtitle className={styles.carId}>Car ID: {car.car_id}</Subtitle>  
                                    </div>  
                                    <div>  
                                        <Body>Status: {car.status}</Body>  
                                        <p className={styles.fleet}>{car.fleet}</p>  
                                    </div>  
                                    {car.distance !== null ? (  
                                        <div className={styles.distanceBlock}>  
                                            <p className={styles.distance}>{car.distance} km</p>  
                                            <p className={styles.distanceLabel}>Distance</p>  
                                        </div>  
                                    ) : (  
                                        <div className={styles.distanceBlock}>  
                                            <p className={styles.distance}>{car.current_geozone}</p>  
                                            <p className={styles.distanceLabel}>Current Geofence</p>  
                                        </div>  
                                    )}  
                                    <div className={styles.buttonBlock}>  
                                        <Button  
                                            size={Size.Small}  
                                            variant={Variant.Outline}  
                                            onClick={(e) => {  
                                                e.stopPropagation();  
                                                handleCarClick(car);  
                                            }}  
                                            disabled={isSearchLoading}  
                                        >  
                                            View Details  
                                        </Button>  
                                    </div>  
                                </div>  
                            </div>  
                            {index < results.length - 1 && <div className={styles.separator} />}  
                        </div>  
                    ))}  
  
                    {results.length > 10 && (  
                        <div className={styles.moreResultsNote}>  
                            <Subtitle>Showing 10 of {results.length} results</Subtitle>  
                        </div>  
                    )}  
                </>  
            );  
        }          
    };  
  
    return (  
        <Card className="card-styles" as="article">  
            <div className={styles.resultsCard}>  
                <div className={styles.header}>  
                    <H3>Search Results</H3>  
                    {isSearchLoading && (  
                        <div className={styles.headerSpinner}>  
                            <Spinner size="small" />  
                            <Body>Searching...</Body>  
                        </div>  
                    )}  
                </div>  
  
                <div className={styles.resultsContainer}>  
                    {renderContent()}  
                </div>  
  
                {isModalOpen && <DetailsComponent onClose={handleCloseModal} />}  
            </div>  
        </Card>  
    );  
};  
  
export default ResultsComponent;  
