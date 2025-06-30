"use client"

import styles from './SideNavComponent.module.css'


const SideNavComponent = ({title = "title", imageName='MongoDBLeafy.svg', isSelected = false}) => {



    return (
        <div className={`${styles.sideNavComponent} ${isSelected ? styles.selected : ''}`}>
            <img src={`/${imageName}`} alt="Logo" width={40} height={40} style={{ marginRight: '10px' }} />
            {title}
        </div>

    );
}

module.exports = SideNavComponent;

