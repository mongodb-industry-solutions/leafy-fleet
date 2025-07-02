'use client';

import { H2 } from '@leafygreen-ui/typography';
import SideNav from '@/components/SideNav/SideNav';
import Link from 'next/link';
import Card from '@leafygreen-ui/card';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import styles from './page.module.css';

export default function Page() {
  return (
    <div>
      <SideNav />
        

      <div className={styles.mainContainer}>
        <div className={styles.headingMargin}>
          <Card className="card-styles" as="article">
            {/* You can put the form fields and the blue box/info inside here */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <H2 >Geospatial Vehicle Search</H2>
            <Button
              variant={Variant.Default}
              darkMode={true}
              size={Size.Default}
              rightGlyph={<Icon glyph="MagnifyingGlass" />}
            >
              Search Vehicles
            </Button>
          </div>
            This is my card component
          </Card>
        </div>
      </div>
    </div>
  );
}
