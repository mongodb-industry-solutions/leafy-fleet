'use client'

import PageHeader from '@/components/PageHeader/PageHeader';
import SideNav from '@/components/SideNav/SideNav';
import ChatComponent from '@/components/ChatComponent/ChatComponent';
import FilterComponent from '@/components/FilterComponent/FilterComponent';

import Link from 'next/link'

import SideNavComponent from '@/components/SideNavComponent/SideNavComponent';


export default function Page() {

    return (
        <div>
            <div>
                <PageHeader />
                <img src="/MongoDBLeafy.svg" alt="Logo" width={120} height={120} style={{ position: 'fixed' }} />
            </div>
            <SideNav>
                <SideNavComponent title="Chat" isSelected='true'/>
                <Link href={`charts`}><SideNavComponent title="Charts"/></Link>
                <Link href={`overview`}><SideNavComponent title="Overview"/></Link>
            </SideNav>
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    marginLeft: '120px', // There should be a better way to do this
                    paddingTop: '120px',
                    height: '100vh',
                }}
            >
                <div style={{ flex: 4 }}>
                    <ChatComponent />
                </div>
                <div style={{ flex: 6 }}>
                    <FilterComponent />
                </div>
            </div>


        </div>
    );
}