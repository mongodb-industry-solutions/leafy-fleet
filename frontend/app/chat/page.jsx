'use client'

import SideNav from '@/components/SideNav/SideNav';
import ChatComponent from '@/components/ChatComponent/ChatComponent';
import FilterComponent from '@/components/FilterComponent/FilterComponent';

import Link from 'next/link'

import SideNavComponent from '@/components/SideNavComponent/SideNavComponent';

export default function Page() {

    return (
        <div>
            
            <SideNav>
                <SideNavComponent title="Chat" isSelected='true'/>
                <Link ><SideNavComponent title="Charts"/></Link>
                <Link href={`overview`}><SideNavComponent title="Overview"/></Link>
            </SideNav>
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    marginLeft: '120px', // There should be a better way to do this
                    height: '90vh',
                }}
            >
                <div style={{ flex: 3 }}>
                    <ChatComponent />
                </div>
                <div style={{ flex: 6 }}>
                    <FilterComponent />
                </div>
            </div>


        </div>
    );
}