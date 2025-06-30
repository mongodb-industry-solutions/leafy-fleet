'use client'

import PageHeader from '@/components/PageHeader/PageHeader';
import SideNav from '@/components/SideNav/SideNav';

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
                <Link href={`chat`}> <SideNavComponent title="Chat" /></Link>
                <SideNavComponent title="Charts" isSelected='true'/>
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
                Charts
            </div>


        </div>
    );
}