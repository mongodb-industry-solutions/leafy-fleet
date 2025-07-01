"use client";
import ExpandableCard from '@leafygreen-ui/expandable-card';
import Checkbox, { getTestUtils } from '@leafygreen-ui/checkbox';
import styles from './FilterComponent.module.css';

const FilterComponent = () => {
  return (
    <div className={styles.filterComponent}>
  {/* First ExpandableCard with 3x 2x2 checkbox groups */}
  <div className={styles.cardWrapper}>
    <ExpandableCard
      title="Filters"
      description=""
      flagText=""
      darkMode={false}
    >
      <div className={styles.filterGrid}>
        <div className={styles.checkboxGroup}>
          <h3 className={styles.groupTitle}>Geofencing</h3>
          <Checkbox data-lgid="cb-1" label="Geofence 1" />
          <Checkbox data-lgid="cb-2" label="Geofence 2" />
          <Checkbox data-lgid="cb-3" label="Downtown " />
          <Checkbox data-lgid="cb-4" label="Norths" />
        </div>
        <div className={styles.checkboxGroup}>
          <h3 className={styles.groupTitle}>Fleet Filter</h3>
          <Checkbox data-lgid="cb-6" label="Fleet 1" />
          <Checkbox data-lgid="cb-7" label="Fleet 2" />
          <Checkbox data-lgid="cb-8" label="Fleet 3" />
        </div>
        <div className={styles.checkboxGroup}>
          <h3 className={styles.groupTitle}>Time</h3>
          
          <Checkbox data-lgid="cb-11" label="All time" />
          <Checkbox data-lgid="cb-12" label="Last hour" />
        </div>
      </div>
    </ExpandableCard>
  </div>

  {/* Additional cards with just description */}
  <div className={styles.cardWrapper}>
    <ExpandableCard
      title="Fleet Overview"
      description=""
      flagText=""
      darkMode={false}
    > 
    <div className={styles.filterGrid}>
      <div><h1>fleet1</h1></div>
    
      
      <div><h1>flee2</h1></div>
    
      <div><h1>fleet3</h1></div>
    </div>
    </ExpandableCard>

  </div>

  <div className={styles.cardWrapper}>
    <ExpandableCard
      title="Agent Run Documents"
      description=""
      flagText=""
      darkMode={false}
    />
  </div>
</div>


    
  );
};

export default FilterComponent;
