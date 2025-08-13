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
                <div style={{  
                flex: 3,  
                position: 'sticky', // Keeps the chat component fixed  
                top: 0, // Applies sticky behavior relative to viewport scroll  
                height: '90vh', // Makes sure it consumes full height  
                overflow: 'hidden', // Prevents scrolling  
            }} >
                    <ChatComponent />
                </div>
                <div style={{  
                flex: 6,  
                height: '90vh', // Controls the division area  
                overflowY: 'auto', // Enables vertical scrolling  
                padding: '0 16px', // Optional padding for internal content  
            }}>
                    <FilterComponent />
                </div>
            </div>


        </div>
    );
}