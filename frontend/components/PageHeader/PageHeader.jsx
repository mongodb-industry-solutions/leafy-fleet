"use client";  
  
import styles from "./PageHeader.module.css";  
import { H1, H3 } from "@leafygreen-ui/typography";  
import { MongoDBLogoMark } from "@leafygreen-ui/logo";  
import InfoWizard from "../InfoWizard/InfoWizard";  
import { useState, useEffect, useRef, useCallback } from "react";  
import talktrackDemo from "@/talkTrack/talkbackBuilder.js";  
import { usePathname } from "next/navigation";  
import { useSelector } from "react-redux";  
  
const PageHeader = () => {  
  const [openHelpModal, setOpenHelpModal] = useState(false);  
  const [showInactivityModal, setShowInactivityModal] = useState(false);  
  const sessionId = useSelector((state) => state.User.sessionId);  
  const isLoggedIn = useSelector((state) => state.User.isLoggedIn);  
  const pathname = usePathname();  
    
  const lastActivityTime = useRef(Date.now());  
  const inactivityTimer = useRef(null);  
  const hasBeenStopped = useRef(false);  
  
  const INACTIVITY_TIMEOUT = 1 * 60 * 1000; // 10 minutes in milliseconds  
  
  // Function to call the stop API  
  const callStopAPI = useCallback(async (useBeacon = false) => {  
    if (hasBeenStopped.current) return;  
      
    hasBeenStopped.current = true;  
      
    try {  
      if (useBeacon && navigator.sendBeacon) {  
        // Use sendBeacon for page unload - more reliable  
        const success = navigator.sendBeacon(  
          "http://localhost:9006/simulation/stop",  
          JSON.stringify({})  
        );  
        console.log("Stop beacon sent:", success);  
      } else {  
        // Regular fetch for other cases  
        await fetch("http://localhost:9006/simulation/stop", {  
          method: "POST",  
          headers: {  
            "Content-Type": "application/json",  
          },  
          // Add keepalive flag for better reliability during unload  
          keepalive: true,  
        });  
        console.log("Stop API called successfully");  
      }  
    } catch (error) {  
      console.error("Error calling stop API:", error);  
    }  
  }, []);  
  
  // Reset inactivity timer  
  const resetInactivityTimer = useCallback(() => {  
    lastActivityTime.current = Date.now();  
      
    if (inactivityTimer.current) {  
      clearTimeout(inactivityTimer.current);  
    }  
      
    if (!hasBeenStopped.current) {  
      inactivityTimer.current = setTimeout(() => {  
        callStopAPI(false); // Don't use beacon for inactivity  
        setShowInactivityModal(true);  
      }, INACTIVITY_TIMEOUT);  
    }  
  }, [callStopAPI]);  
  
  // Handle user activity events  
  const handleUserActivity = useCallback(() => {  
    resetInactivityTimer();  
  }, [resetInactivityTimer]);  
  
  // Handle page visibility change  
  const handleVisibilityChange = useCallback(() => {  
    if (document.hidden) {  
      const timeSinceLastActivity = Date.now() - lastActivityTime.current;  
        
      if (timeSinceLastActivity >= INACTIVITY_TIMEOUT) {  
        callStopAPI(false);  
        setShowInactivityModal(true);  
      }  
    } else {  
      handleUserActivity();  
    }  
  }, [callStopAPI, handleUserActivity]);  
  
  // Handle page unload - use beacon for better reliability  
  const handleBeforeUnload = useCallback(() => {  
    callStopAPI(true); // Use beacon for page unload  
  }, [callStopAPI]);  
  
  // Additional unload handler for better coverage  
  const handleUnload = useCallback(() => {  
    callStopAPI(true);  
  }, [callStopAPI]);  
  
  // Page focus/blur handlers for additional coverage  
  const handlePageBlur = useCallback(() => {  
    // Set a short timer - if page doesn't regain focus, assume user left  
    setTimeout(() => {  
      if (document.hidden || !document.hasFocus()) {  
        callStopAPI(true);  
      }  
    }, 1000);  
  }, [callStopAPI]);  
  
  useEffect(() => {  
    if (isLoggedIn && ['/chat', '/overview', '/charts'].some(path => pathname.endsWith(path))) {  
      const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];  
        
      activityEvents.forEach(event => {  
        document.addEventListener(event, handleUserActivity, true);  
      });  
  
      document.addEventListener('visibilitychange', handleVisibilityChange);  
      window.addEventListener('beforeunload', handleBeforeUnload);  
      window.addEventListener('unload', handleUnload);  
      window.addEventListener('blur', handlePageBlur);  
        
      resetInactivityTimer();  
  
      return () => {  
        activityEvents.forEach(event => {  
          document.removeEventListener(event, handleUserActivity, true);  
        });  
          
        document.removeEventListener('visibilitychange', handleVisibilityChange);  
        window.removeEventListener('beforeunload', handleBeforeUnload);  
        window.removeEventListener('unload', handleUnload);  
        window.removeEventListener('blur', handlePageBlur);  
          
        if (inactivityTimer.current) {  
          clearTimeout(inactivityTimer.current);  
        }  
      };  
    }  
  }, [isLoggedIn, pathname, handleUserActivity, handleVisibilityChange, handleBeforeUnload, handleUnload, handlePageBlur, resetInactivityTimer]);  
  
  const handleRefresh = () => {  
    window.location.reload();  
  };  
  
  return (  
    <>  
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
  
      {showInactivityModal && (  
        <div className={styles.modalOverlay}>  
          <div className={styles.modal}>  
            <h2>Demo Stopped Due to Inactivity</h2>  
            <p>Your session has been stopped due to 10 minutes of inactivity.</p>  
            <p>Please refresh to continue.</p>  
            <button onClick={handleRefresh} className={styles.refreshButton}>  
              Refresh to Continue  
            </button>  
          </div>  
        </div>  
      )}  
    </>  
  );  
};  
  
export default PageHeader;  
