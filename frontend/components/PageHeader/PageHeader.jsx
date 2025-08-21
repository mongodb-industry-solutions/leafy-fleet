"use client";  
  
import styles from "./PageHeader.module.css";  
import { H1, H3 } from "@leafygreen-ui/typography";  
import { MongoDBLogoMark } from "@leafygreen-ui/logo";  
import InfoWizard from "../InfoWizard/InfoWizard";  
import { useState, useEffect, useRef, useCallback } from "react";  
import talktrackDemo from "@/talkTrack/talkbackBuilder.js";  
import { usePathname } from "next/navigation";  
import { useSelector } from "react-redux";  
import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';

const PageHeader = () => {  
  const [openHelpModal, setOpenHelpModal] = useState(false);  
  const [showInactivityModal, setShowInactivityModal] = useState(false);  
  const sessionId = useSelector((state) => state.User.sessionId);  
  const isLoggedIn = useSelector((state) => state.User.isLoggedIn);  
  const pathname = usePathname();  
    
  const lastActivityTime = useRef(Date.now());  
  const inactivityTimer = useRef(null);  
  const [hasBeenStopped, setHasBeenStopped] = useState(false);  
  const [pausedByButton, setPausedByButton] = useState(false); // Add this new state  

  const visibilityTimer = useRef(null); 

  
  const INACTIVITY_TIMEOUT =  60 * 5 * 1000; // 5 minutes in milliseconds  
  
  // Function to call the stop API , to not pause if multiple users just calls to reduce user by 1, if user count is 0 then stop the simulation
  const callStopAPI = useCallback(async ( isManualStop = false) => {  
  if (hasBeenStopped) return;  
  try {  
    await fetch(`http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/simulation/reduce-users`, {  
      method: "POST",  

      keepalive: true,  
    });  
    console.log("Stop API called successfully");  
    setHasBeenStopped(true); 
    if (isManualStop) {  
      setPausedByButton(true);  
    }  
  } catch (error) {  
    console.error("Error calling stop API:", error);  
  }  
}, [hasBeenStopped]);   


  const [copied, setCopied] = useState(false);  


  const handleCopySessionId = async () => {  
  try {  
    await navigator.clipboard.writeText(sessionId);  
    setCopied(true);  
    setTimeout(() => setCopied(false), 2000);  
  } catch (err) {  
    console.error('Failed to copy:', err);  
  }  
};  
  
  // Reset inactivity timer  
  const resetInactivityTimer = useCallback(() => {  
    lastActivityTime.current = Date.now();  
      
    if (inactivityTimer.current) {  
      clearTimeout(inactivityTimer.current);  
    }  
      
    if (!hasBeenStopped) {  
      inactivityTimer.current = setTimeout(() => {  
        callStopAPI();  
        setShowInactivityModal(true);  
      }, INACTIVITY_TIMEOUT);  
    }  
  }, [callStopAPI]);  
  
  // Handle user activity events  
  const handleUserActivity = useCallback(() => {  
    if (!document.hidden) { // Only reset if page is visible  
      resetInactivityTimer();  
    }  
  }, [resetInactivityTimer]);  
  
  // Handle page visibility change  
  const handleVisibilityChange = useCallback(() => {  
    if (document.hidden) {  
      // Page became hidden - start the 5-minute countdown  
      if (visibilityTimer.current) {  
        clearTimeout(visibilityTimer.current);  
      }  
        
      visibilityTimer.current = setTimeout(() => {  
        callStopAPI();  
        setShowInactivityModal(true);  
      }, INACTIVITY_TIMEOUT);  
        
    } else {  
      // Page became visible again - cancel the countdown and reset activity  
      if (visibilityTimer.current) {  
        clearTimeout(visibilityTimer.current);  
        visibilityTimer.current = null;  
      }  
      handleUserActivity();  
    }  
  }, [callStopAPI, handleUserActivity]);  
  
  useEffect(() => {  
    if (isLoggedIn && ['/chat', '/geosearch', '/charts'].some(path => pathname.endsWith(path))) {  
      const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];  
        
      activityEvents.forEach(event => {  
        document.addEventListener(event, handleUserActivity, true);  
      });  
  
      document.addEventListener('visibilitychange', handleVisibilityChange);  
        
      resetInactivityTimer();  
  
      return () => {  
        activityEvents.forEach(event => {  
          document.removeEventListener(event, handleUserActivity, true);  
        });  
          
        document.removeEventListener('visibilitychange', handleVisibilityChange);  
          
        if (inactivityTimer.current) {  
          clearTimeout(inactivityTimer.current);  
        }  
          
        if (visibilityTimer.current) {  
          clearTimeout(visibilityTimer.current);  
        }  
      };  
    }  
  }, [isLoggedIn, pathname, handleUserActivity, handleVisibilityChange, resetInactivityTimer]);  
  
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
  
          {isLoggedIn && ['/chat', '/geosearch', '/charts'].some(path => pathname.endsWith(path)) &&  

            <div className= {styles.horizontalContainer}>
              <div className={styles.buttonContainer}>
                <Button    
                  variant={Variant.Primary}    
                  darkMode={false}    
                  size={Size.Default}    
                  rightGlyph={<Icon glyph="Stop" />}    
                  onClick={() => callStopAPI(true)}  // Add arrow function  
                >    
                  {hasBeenStopped ? "Simulation Stopped" : "Stop Simulation"}    
                </Button>  

            </div>
           
            <div className={styles.sessionIdContainer}>
                {sessionId && ( 
                  <div className={styles.sessionIdText}> 
                    SessionID:
                  <div   
                      className={`${styles.sessionIdButton} ${copied ? styles.copied : ''}`}  
                      //onClick={handleCopySessionId}  
                    >  
            
                  <code className={styles.sessionIdValue}>{sessionId}</code>  
                    {/*
                      <span className={styles.copyIcon}>
                        {copied ? '✓' : '📋 '}      
                      </span>   
                     */}  
                </div> 
                </div> )}
            </div>
          </div>
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
  
      {showInactivityModal && !pausedByButton &&(  
        <div className={styles.modalOverlay}>  
          <div className={styles.modal}>  
            <h2>Demo Stopped Due to Inactivity</h2>  
            <p>Your session has been stopped due to 5 minutes of inactivity.</p>  
            {sessionId && (  
              <div   
                  className={`${styles.sessionIdButton} ${copied ? styles.copied : ''}`}  
                  //onClick={handleCopySessionId}  
                >  
               <code className={styles.sessionIdValue}>{sessionId}</code>  
                {/*
                      <span className={styles.copyIcon}>
                        {copied ? '✓' : '📋 '}      
                      </span>   
                     */}  
              </div>  )}
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
