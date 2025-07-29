"use client";

import styles from "./SideNav.module.css";
import { SideNav, SideNavItem } from "@leafygreen-ui/side-nav";
import { usePathname } from "next/navigation";
import Link from "next/link";

const SideNavigation = () => {
  const pathname = usePathname();

  return (
    <SideNav
      widthOverride={120}
      className={styles.sideNav}
      aria-label="Main navigation"
    >
      <Link
        href="/chat"
        className={
          pathname === "/chat"
            ? `${styles.sideBarButton} ${styles.activeNavItem}`
            : styles.sideBarButton
        }
      >
        <SideNavItem>Chat</SideNavItem>
      </Link>

      <Link
        href="/charts"
        className={
          pathname === "/charts"
            ? `${styles.sideBarButton} ${styles.activeNavItem}`
            : styles.sideBarButton
        }
      >
        <SideNavItem>Charts</SideNavItem>
      </Link>

      <Link
        href="/overview"
        className={
          pathname === "/overview"
            ? `${styles.sideBarButton} ${styles.activeNavItem}`
            : styles.sideBarButton
        }
      >
        <SideNavItem>Overview</SideNavItem>
      </Link>

      <Link
        href="/"
        className={
          pathname === "/"
            ? `${styles.sideBarButton} ${styles.activeNavItem}`
            : styles.sideBarButton
        }
      >
        <SideNavItem>Read the Docs</SideNavItem>
      </Link>
    </SideNav>
  );
};

export default SideNavigation;
