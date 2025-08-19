"use client";

import Card from '@leafygreen-ui/card';
import { H2, H3 } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import { Combobox, ComboboxOption,ComboboxGroup } from '@leafygreen-ui/combobox';
import styles from './OverviewCard.module.css';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedType, setSelectedFleets, setGeoFences, setMaxDistance, setMinDistance, setLocation, setIsLoading } from  '@/redux/slices/OverviewSlice';
import dynamic from 'next/dynamic';
import Banner from '@leafygreen-ui/banner';
import { NumberInput } from '@leafygreen-ui/number-input';
import { setResults } from '@/redux/slices/ResultSlice';
import { geospatialAPI } from './geospatialAPI';


// Dynamically import components that might use browser APIs
const CodeComponent = dynamic(() => import('../CodeComponet/CodeComponent.jsx'), { ssr: false });
const ResultsComponent = dynamic(() => import('../ResultsComponent/ResultsComponent'), { ssr: false });
const OverviewCard = () => {

    // State to manage the selected option for the geospatial search
    const dispatch = useDispatch();
    const selectedType = useSelector(state => state.Overview.type);
    const fleetsFilter = useSelector(state => state.Overview.fleetsFilter);
    const geoFences = useSelector(state => state.Overview.geoFences);
    const location = useSelector(state => state.Overview.location);
    const maxDistance = useSelector(state => state.Overview.maxDistance);
    const minDistance = useSelector(state => state.Overview.minDistance);
    const sessionId = useSelector(state => state.User.sessionId);
    const fleet1Name = useSelector(state => state.User.fleet1Name);
    const fleet2Name = useSelector(state => state.User.fleet2Name);
    const fleet3Name = useSelector(state => state.User.fleet3Name);
    const selectedFleets = useSelector(state => state.User.selectedFleets);
    const all_geofences = useSelector(state=> state.Geofences.all_geofences);

    const getFleetName = (carId) => {  
      if (carId >= 1 && carId <= 100) {  
          return fleet1Name;  
      } else if (carId >= 101 && carId <= 200) {  
          return fleet2Name;  
      } else if (carId >= 201 && carId <= 300) {  
          return fleet3Name;  
      } else {  
          return `Fleet ${Math.floor(carId/100) + 1}`; // Fallback for car_ids outside expected ranges  
      }  
    };  
    const handleSearch = async () => {

        if (!location && selectedType === "nearest" || geoFences.length === 0 && selectedType === "inside") {
            alert("Please select a geofence or location to search.");
            return;
        }
        dispatch(setIsLoading({ isLoading: true })); // Set loading state to true
        try {
            let results;
            if (selectedType === "nearest") {
            results = await geospatialAPI.searchNearestVehicles({
                sessionId,
                location,
                minDistance,
                maxDistance,
                fleetsFilter

            });
            } else {
            results = await geospatialAPI.searchInsideVehicles({
                sessionId,
                geoFences,
                fleetsFilter
            });
            }

        // Transform results, excluding metadata but keeping all other fields
        const formattedResults = results.map(({ metadata, ...rest }) => ({
            ...rest, // Spread all fields except metadata
            status: getCarStatus(rest), // Add status based on car state
            fleet: getFleetName(rest.car_id),
            distance: rest.distance_to_geofence ? 
                (rest.distance_to_geofence/1000).toFixed(2) : null
            }));

            console.log('Formatted results:', formattedResults);
            dispatch(setResults({ results: formattedResults }));
        } catch (error) {
            console.error('Search failed:', error);
            dispatch(setResults({ results: [] }));
        } finally {
            dispatch(setIsLoading({ isLoading: false })); // Set loading state to false
        }
    };


  const getCarStatus = (car) => {
    if (car.is_crashed) return "Issue";
    if (car.is_oil_leak) return "Maintenance";
    if (car.is_engine_running) return "Active";
    return "Issue";
  };

  return (
    <div>
      <Card className={styles.overviewCard}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <H3>Geospatial Vehicle Search {fleet1Name}</H3> 
          <Button
            variant={Variant.BaseGreen}
            darkMode={false}
            size={Size.Default}
            rightGlyph={<Icon glyph="MagnifyingGlass" />}
            onClick={handleSearch}
            disabled={!selectedType || (selectedType === "nearest" && !location) || (selectedType === "inside" && geoFences.length === 0)}
          >
            Search Vehicles
          </Button>
        </div>

            <div className={styles.topComboboxes}> 
            <Combobox
                label="Search Type"
                description="Select type of geospatial search"
                placeholder=""
                initialValue={selectedType}
                clearable={false}
                onChange={(value) => {
                    dispatch(setSelectedType({type: value}));
                }}
            >
                <ComboboxOption value="inside" displayName='Inside Geofence'/>
                <ComboboxOption value="nearest" displayName='Nearest' />

            </Combobox>

            <Combobox
                label="Fleets Selected"
                description="Optional"
                placeholder="Choose if you want to filter by fleet"
                multiselect={true}
                initialValue={fleetsFilter}
                onChange={fleets => {
                    // Convert selected fleet strings to integers
                    const fleetNumbers = fleets ? fleets.map(f => parseInt(f, 10)) : [];
                    console.log('Selected fleet numbers:', fleetNumbers);
                    dispatch(setSelectedFleets({ fleets: fleetNumbers }));
                }}
            >
                <ComboboxOption value="1" displayName={fleet1Name} />
                {selectedFleets>1 && 
                <ComboboxOption value="2" displayName={fleet2Name} />}
                {selectedFleets>2 &&
                <ComboboxOption value="3" displayName={fleet3Name}/>}
            </Combobox>

            {selectedType==="inside" && 
            <Combobox
                label="Geofences"
                description="Select the geofences to use for the search"
                placeholder="Select geofences"
                multiselect={true}
                initialValue={geoFences}
                onChange={zone => {
                    console.log('Selected geofences:', zone);
                    dispatch(setGeoFences({ geoFences: zone || [] }));
                }}>
                {all_geofences.map(geofence => (  
              <ComboboxOption   
                key={geofence.name}   
                value={geofence.name}   
                displayName={geofence.displayName || geofence.name}   
              />  
            ))}  
            </Combobox>
            }

            {selectedType==="nearest" &&
            
            <Combobox
                label="Geofences"
                description="Select the geofence to use for the search"
                placeholder="Select the geofence"
                multiselect={false}
                initialValue={location}
                onChange={loc => {
                    dispatch(setLocation({ location: loc || null }));
                }}>
                {all_geofences.map(geofence => (  
              <ComboboxOption   
                key={`nearest-${geofence.name}`} 
                value={geofence.name}   
                displayName={geofence.displayName || geofence.name}   
              />  
            ))}  
            </Combobox>
          }
            </div>
            {selectedType==="nearest" && 
            <div className={styles.midComboboxes}> 
            
            <NumberInput 
                label="Min Distance"
                description="Minimum distance to search"
                value={minDistance}
                unit="meters"
                min={0}
                onChange={e => {
                    const num = Number(e.target.value);
                    if (!isNaN(num)) {
                    dispatch(setMinDistance({ minDistance: num }));
                    } else {
                    dispatch(setMinDistance({ minDistance: 0 }));
                    }
                }}
            />
             <NumberInput 
                label="Max Distance"
                description="Maximun distance to search on"
                value={maxDistance}
                unit="meters"
                min={0}
                onChange={e => {
                    const num = Number(e.target.value);
                    if (!isNaN(num)) {
                    dispatch(setMaxDistance({ maxDistance: num }));
                    } else {
                    dispatch(setMaxDistance({ maxDistance: 0 }));
                    }
                }}
            />

    
            </div>
            }
            <CodeComponent/> <br />
            {selectedType === "nearest" ? (
                <Banner> <strong>Nearest Vehicles</strong> <br /> Find vehicles closest to the center of a specific geofence, ordered by distance.</Banner>
                ): (<Banner> <strong>Inside Geofence</strong> <br /> Find vehicles completely within a specified geofence boundary</Banner>)}

          </Card> <br />
         
          <br />
          <ResultsComponent />
        </div>
  );
};

export default OverviewCard;