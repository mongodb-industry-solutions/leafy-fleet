"use client";

import { useDispatch, useSelector } from 'react-redux';
import LoginComp from "../login/LoginComp";
import styles from "./LoginManager.module.css";
import { setSelectedUser } from '@/redux/slices/UserSlice';

const LoginManager = () => {

const dispatch = useDispatch();
const isSelectedUser = useSelector(state => state.User.selectedUser.userName)

    // console.log("LoginManager isSelectedUser", isSelectedUser)

    const modalObserver = () => {

        if (isSelectedUser) {
            // Trigger something to toggle the fleet construction modal
        }

    }

return (<>

    <LoginComp modalObserver={modalObserver} />
    
    

    </>);
};

module.exports = LoginManager;