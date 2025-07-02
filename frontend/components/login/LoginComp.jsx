"use client"

import React, { useState, useEffect } from 'react';
import Icon from '@leafygreen-ui/icon';
import { Modal, Container } from 'react-bootstrap';
import { H2, Subtitle, Description } from '@leafygreen-ui/typography';

import styles from "./loginComp.module.css";
import UserComp from '../user/UserComp';
import Banner from '@leafygreen-ui/banner';
import WizardIcon from '@leafygreen-ui/icon/dist/Wizard';
import { USER_MAP } from '@/lib/constants';


const LoginComp = (props) => {
    const [open, setOpen] = useState(false);
    
    useEffect(() => {
        setOpen(true);
    }, []);
  
    const handleClose = () => {
        setOpen(false)
    }

    return (
        <Modal
            show={open}
            onHide={handleClose}
            size="lg"
            aria-labelledby="contained-modal-title-vcenter"
            centered
            fullscreen={'md-down'}
            className={styles.leafyFeel}
            backdrop="static"
        >
            <Container className='p-3 h-100'>
                {/*
                <div className='d-flex flex-row-reverse p-1 cursorPointer' onClick={handleClose}>
                    <Icon glyph="X" />
                </div>
               */}
               
                <div className={styles.modalMainCOntent}>
                    <H2 className={styles.centerText}>Welcome to Leafy Fleet</H2>
                    <Subtitle className={`${styles.weightNormal} ${styles.centerText} mt-2`}>This is a MongoDB demo</Subtitle>
                    <br/>
                    <Description className={styles.descriptionModal}>
                        Please select the user you would like to login as
                    </Description>
                    <div className={`${styles.usersContainer}`}>
                        {
                            USER_MAP.map((user, index) => (
                                <UserComp 
                                    key={index} 
                                    user={user} 
                                    setOpen={setOpen}
                                ></UserComp>
                            ))
                        }
                    </div>
                    <Banner variant='info' className='mb-2'>
                        Look out for <WizardIcon></WizardIcon> to find out more about what is going on behind the scenes!
                    </Banner>
                    <Description className={`${styles.descriptionModal} mb-3`}>
                        Note: Each user has pre-loaded data, such as past orders and items in their cart, with content unique to them. This variation is designed to showcase different scenarios, providing a more dynamic and realistic user experience for the demo.
                    </Description>
                </div>
            </Container>
        </Modal>
    )
}

export default LoginComp;