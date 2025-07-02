'use client'

import SideNav from '@/components/SideNav/SideNav';
import ChatComponent from '@/components/ChatComponent/ChatComponent';
import FilterComponent from '@/components/FilterComponent/FilterComponent';

import Link from 'next/link'


export default function Page() {

    return (
        <div>            
            <SideNav />
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