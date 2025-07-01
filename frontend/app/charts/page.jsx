'use client'

import SideNavigation from '@/components/SideNav/SideNav';


export default function Page() {

    return (
        <div>
            
            <SideNavigation />


            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    marginLeft: '120px', // There should be a better way to do this
                    height: '100vh',
                }}
            >
                Charts
            </div>


        </div>
    );
}