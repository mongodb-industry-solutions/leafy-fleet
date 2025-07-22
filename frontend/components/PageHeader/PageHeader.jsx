'use client';

import styles from './PageHeader.module.css';
import { H1 } from '@leafygreen-ui/typography';
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import {
  MongoDBLogo,
  MongoDBLogoMark,
  
} from '@leafygreen-ui/logo';
import InfoWizard from '../InfoWizard/InfoWizard';
import { useState } from 'react';
import { chatbotTalktrackSection } from '@/talkTrack/chatbotTalktrack';
import talktrackDemo from '@/talkTrack/talckBackDemo.js';

const PageHeader = () => {

  const [openHelpModal, setOpenHelpModal] = useState(false);

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
        <InfoWizard
        open={openHelpModal}
        setOpen={setOpenHelpModal}
        tooltipText="Tell me more!"
        iconGlyph="Wizard" 
        sections={talktrackDemo()}
        />

      </div>
    </header>
  );
};

export default PageHeader;



