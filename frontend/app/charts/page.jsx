'use client'

import SideNavigation from '@/components/SideNav/SideNav';

import ChartsComponent from '@/components/ChartsComponent/ChartsComponent';

export default function Page() {

    return (
        <div>
            
            <SideNavigation />


            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                    marginLeft: '120px', // There should be a better way to do this
                    height: '90vh',
                }}
            >
                <ChartsComponent />
            </div>


        </div>
    );
}