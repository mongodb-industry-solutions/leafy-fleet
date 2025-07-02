
"use client"

import React from 'react';
import { Body } from '@leafygreen-ui/typography';
import Card from '@leafygreen-ui/card';
import { Skeleton } from '@leafygreen-ui/skeleton-loader';

import styles from "./userComp.module.css";
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedUser } from '@/redux/slices/UserSlice';

const UserComp = (props) => {
    const {
        user = null, 
        handleClose, 
    } = props;
    const dispatch = useDispatch()
    const isSelectedUser = useSelector(state => state.User.selectedUser?._id === user._id)

    const selectUserLocally = () => {
        dispatch(setSelectedUser({user: user}))
    }
    const selectUserAndCloseModal = () => {
        dispatch(setSelectedUser({user: user}))
        handleClose()
    }

    return (
        <Card 
            className={`${styles.userCard} ${user !== null ? 'cursorPointer' : ''} ${isSelectedUser ? styles.userSelected : ''}`}
            onMouseEnter={() => selectUserLocally()}
            onClick={() => selectUserAndCloseModal()}
        >
            {
                user === null
                ? <Skeleton></Skeleton>
                : <>
                    <img src={`/rsc/users/${user._id}.png`}></img>
                    <Body className={styles.userName}>{user.name}</Body>
                    <Body className={styles.message}>{user.message}</Body>
                </>
            }

        </Card>
    );
};

export default UserComp;