'use client'

import PageHeader from '@/components/PageHeader/PageHeader';
import SideNavigation from '@/components/SideNav/SideNav';


export default function Page() {

    return (
        <div>
            <div>
                <PageHeader />
                <img src="/MongoDBLeafy.svg" alt="Logo" width={120} height={120} style={{ position: 'fixed' }} />
            </div>
            <SideNavigation />


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