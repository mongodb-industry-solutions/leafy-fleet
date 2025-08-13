"use client";

import styles from "./PageHeader.module.css";
import { H1, H3 } from "@leafygreen-ui/typography";
import { MongoDBLogoMark } from "@leafygreen-ui/logo";
import InfoWizard from "../InfoWizard/InfoWizard";
import { useState } from "react";
import talktrackDemo from "@/talkTrack/talkbackBuilder.js";
import { usePathname } from "next/navigation";
import { useSelector } from "react-redux";

const PageHeader = () => {
  const [openHelpModal, setOpenHelpModal] = useState(false);
  const sessionId = useSelector((state) => state.User.sessionId);
  const isLoggedIn = useSelector((state) => state.User.isLoggedIn);
  const pathname = usePathname();

  return (
    <header className={styles.wrapper}>
      <div className={styles.leftLogo}>
        <MongoDBLogoMark height={70} width={70} color="green-base" />
      </div>

      <div className={styles.center}>
        <img
          src="/General_INDUSTRY_Auto10x.png"
          alt=""
          width={70}
          height={70}
        />

        <H1>Leafy Fleet</H1>

       {isLoggedIn && ['/chat', '/overview', '/charts'].some(path => pathname.endsWith(path)) &&  
        <H3>Session ID: {sessionId}</H3>  
      }  
      </div>


      <div className={styles.right}>
        <InfoWizard
          open={openHelpModal}
          setOpen={setOpenHelpModal}
          tooltipText="Tell me more!"
          iconGlyph="Wizard"
          sections={talktrackDemo(pathname)}
        />
      </div>
    </header>
  );
};

export default PageHeader;
