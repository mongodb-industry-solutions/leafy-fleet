"use client";

import Card from '@leafygreen-ui/card';
import { H2, H3 } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import { Combobox, ComboboxOption,ComboboxGroup } from '@leafygreen-ui/combobox';
import styles from './OverviewCard.module.css';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedType, setSelectedFleets, setGeoFences, setMaxDistance, setMinDistance, setLocation } from  '@/redux/slices/OverviewSlice';
import dynamic from 'next/dynamic';
import Banner from '@leafygreen-ui/banner';
import { NumberInput } from '@leafygreen-ui/number-input';
import { setResults } from '@/redux/slices/ResultSlice';
import { geospatialAPI } from './geospatialAPI';
import { geofences } from '@/components/Geofences/geofences'; // Import the geofences data  

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

    const handleSearch = async () => {
    try {
      let results;
      if (selectedType === "nearest") {
        results = await geospatialAPI.searchNearestVehicles({
          sessionId,
          location,
          minDistance,
          maxDistance
        });
      } else {
        results = await geospatialAPI.searchInsideVehicles({
          sessionId,
          geoFences
        });
      }

      // Transform API results to match ResultsComponent format
      const formattedResults = results.map(car => ({
        id: car.car_id,
        driver: `Car ${car.car_id}`,
        fleet: `Fleet ${Math.floor(car.car_id/100) + 1}`,
        distance: car.distance_to_geofence ? 
          (car.distance_to_geofence/1000).toFixed(2) : null,
        status: getCarStatus(car),
        // Include all original data for details view
        details: car
      }));

      dispatch(setResults({ results: formattedResults }));
    } catch (error) {
      console.error('Search failed:', error);
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
          <H3>Geospatial Vehicle Search</H3>
          <Button
            variant={Variant.Default}
            darkMode={true}
            size={Size.Default}
            rightGlyph={<Icon glyph="MagnifyingGlass" />}
            onClick={handleSearch}
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
                onChange={fleets => dispatch(setSelectedFleets({ fleets }))}
            >
                <ComboboxOption value="fleet1" displayName='Fleet 1' />
                <ComboboxOption value="fleet2" displayName='Fleet 2'/>
                <ComboboxOption value="fleet3" displayName='Fleet 3'/>
                <ComboboxOption value="fleet4" displayName='Fleet 4' disabled={true}/>
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
                <ComboboxOption value="downtown" displayName='Downtown' />
                {geofences.map(geofence => (  
              <ComboboxOption   
                key={geofence._id}   
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
                <ComboboxOption value="downtown" displayName='Downtown' />
                <ComboboxOption value="riverside" displayName='Riverside' />
                <ComboboxOption value="barton_creek" displayName='Barton Creek' />
                <ComboboxOption value="georgetown" displayName='Georgetown' />
                <ComboboxOption value="north_austin" displayName='North Austin' />
                <ComboboxOption value="east_austin" displayName='East Austin' />
                <ComboboxOption value="west_austin" displayName='West Austin' />
                <ComboboxOption value="south_austin" displayName='South Austin' />
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