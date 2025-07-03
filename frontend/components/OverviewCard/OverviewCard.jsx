"use client"

import Card from '@leafygreen-ui/card';
import { H2, H3 } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import { Combobox, ComboboxOption,ComboboxGroup } from '@leafygreen-ui/combobox';
import styles from './OverviewCard.module.css';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedType, setSelectedFleets, setGeoFences, setMaxDistance, setMinDistance, setLocation } from  '@/redux/slices/OverviewSlice';
import CodeComponent from '../CodeComponet/CodeComponent.jsx';
import Banner from '@leafygreen-ui/banner';
import { NumberInput } from '@leafygreen-ui/number-input';

const OverviewCard = () => {

    // State to manage the selected option for the geospatial search
    const dispatch = useDispatch();
    const selectedType = useSelector(state => state.Overview.type);
    const fleetsFilter = useSelector(state => state.Overview.fleetsFilter);
    const geoFences = useSelector(state => state.Overview.geoFences);
    const location = useSelector(state => state.Overview.location);
    const maxDistance = useSelector(state => state.Overview.maxDistance);
    const minDistance = useSelector(state => state.Overview.minDistance);
  return (
<div> 
<Card className="card-styles" as="article">
            {/* You can put the form fields and the blue box/info inside here */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' ,  }}>
            <H3 >Geospatial Vehicle Search</H3>
            <Button
              variant={Variant.Default}
              darkMode={true}
              size={Size.Default}
              rightGlyph={<Icon glyph="MagnifyingGlass" />}
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
                <ComboboxOption value="zone1" displayName='Zone 1' />
                <ComboboxOption value="zone2" displayName='Zone 2' />
                <ComboboxOption value="zone3" displayName='Zone 3' />
            </Combobox>
            }

            {selectedType==="nearest" &&
            
            <Combobox
                label="Geofencees"
                description="Select the geofence to use for the search"
                placeholder="Select the geofence"
                multiselect={false}
                initialValue={location}
                onChange={loc => {
                    dispatch(setLocation({ location: loc || null }));
                }}>
                <ComboboxOption value="zone1" displayName='Zone 1' />
                <ComboboxOption value="zone2" displayName='Zone 2' />
                <ComboboxOption value="zone3" displayName='Zone 3' />
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
                    console.log('Min Distance changed:', e.target.value);
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
                <Banner> <strong>Nearest Vehicles</strong> <br /> Find vehicles closest to a specific point, ordered by distance</Banner>
                ): (<Banner> <strong>Inside Geofence</strong> <br /> Find vehicles completely within a specified geofence boundary</Banner>)}

          </Card>
          

          </div>
  );
};

export default OverviewCard;