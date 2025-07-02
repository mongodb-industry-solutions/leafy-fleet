'use client';

import styles from './PageHeader.module.css';
import { H1 } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import {
  MongoDBLogo,
  MongoDBLogoMark,
  
} from '@leafygreen-ui/logo';

const PageHeader = () => {
  return (
    

    <header className={styles.wrapper}>
        <div className={styles.leftLogo}> 
        <MongoDBLogoMark height={70} width={70} color='green-base' />
        </div>
        
      <div className={styles.center}>
        <img src="/General_INDUSTRY_Auto10x.png" alt="" width={70} height={70}/>

        <H1>Leafy Fleet</H1>
      </div>

      <div className={styles.right}>
        <Button
          variant={Variant.Default}
          darkMode={false}
          size={Size.Default}
          leftGlyph={<Icon glyph="Wizard" />}
        >
          Tell me more!
        </Button>
      </div>
    </header>
  );
};

export default PageHeader;
