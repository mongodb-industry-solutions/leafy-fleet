"use client"

import styles from './SideNav.module.css'



const SideNav = ({ children }) => {
    return (
        <div className={styles.sideNav} >
            {children}
        </div>

    );
}

export default SideNav;