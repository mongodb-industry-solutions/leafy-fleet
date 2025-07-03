'use client';

import SideNav from '@/components/SideNav/SideNav';
import styles from './page.module.css';
import OverviewCard from '@/components/OverviewCard/OverviewCard';

export default function Page() {
  return (
    <div>
      <SideNav />

      <div className={styles.mainContainer}>
        <div className={styles.headingMargin}>
          <OverviewCard/>
        </div>
      </div>
    </div>
  );
}
