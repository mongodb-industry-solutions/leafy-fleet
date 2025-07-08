"use client";

import styles from "./SideNav.module.css";

import { SideNav, SideNavGroup, SideNavItem } from "@leafygreen-ui/side-nav";

import Link from "next/link";

const SideNavigation = ({ children }) => {
  return (
    <SideNav
      widthOverride={120}
      className={styles.sideNav}
      aria-label="Main navigation"
    >
      <Link href={`chat`} className={styles.sideBarButton}>
        <SideNavItem>Chat</SideNavItem>
      </Link>
      <Link href={`charts`} className={styles.sideBarButton}>
        <SideNavItem>Charts</SideNavItem>
      </Link>
      <Link href={`overview`} className={styles.sideBarButton}>
        <SideNavItem>Overview</SideNavItem>
      </Link>
      <Link href={`docs`} className={styles.sideBarButton}>
        <SideNavItem>Read the Docs</SideNavItem>
      </Link>
    </SideNav>
  );
};

export default SideNavigation;
