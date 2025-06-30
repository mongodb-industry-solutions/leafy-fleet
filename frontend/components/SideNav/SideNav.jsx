"use client"

import styles from './SideNav.module.css'

import { SideNav, SideNavGroup, SideNavItem } from '@leafygreen-ui/side-nav';

import Icon from "@leafygreen-ui/icon";

import Link from 'next/link'

const SideNavigation = ({ children }) => {
    return (
    <SideNav
    widthOverride={120}
    className={styles.sideNav}
  >
    <Link href={`chat`}><SideNavItem>Chat</SideNavItem></Link>
    <Link href={`charts`}><SideNavItem>Charts</SideNavItem></Link>
    <Link href={`overview`}><SideNavItem>Overview</SideNavItem></Link>
    <Link href={`docs`}><SideNavItem>Read the Docs</SideNavItem></Link>
  </SideNav>

    );
}

export default SideNavigation;