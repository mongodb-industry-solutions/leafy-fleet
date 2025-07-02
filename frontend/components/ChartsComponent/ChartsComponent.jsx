"use client";

import styles from './ChartsComponent.module.css';
import InfoCardComponent from '@/components/InfocardComponent/InfocardComponent';

const ChartsComponent = () => {
    return (
        <div className={styles.container}>
            <div className={styles.topPart} style={{ flex: 1 }}>
                <InfoCardComponent title="Chart 1" />
                <InfoCardComponent title="Chart 2" />
                <InfoCardComponent title="Chart 3" />
            </div>
            <div className={styles.bottomPart} style={{ flex: 5 }}>

                <iframe
                    src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=3bb18da5-6d6a-43d8-aa0d-8924eefc58cd&maxDataAge=3600&theme=light&autoRefresh=true"
                    width="550"
                    height="400"
                    style={{
                        background: '#FFFFFF',
                        border: 'none',
                        borderRadius: '2px',
                        boxShadow: '0 2px 10px 0 rgba(70, 76, 79, 0.2)'
                    }}
                    title="My Iframe"
                />

                <iframe
                    src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=eae4af4e-6804-4c48-8bde-d06ef567183e&maxDataAge=3600&theme=light&autoRefresh=true"
                    width="550"
                    height="400"
                    style={{
                        background: '#FFFFFF',
                        border: 'none',
                        borderRadius: '2px',
                        boxShadow: '0 2px 10px 0 rgba(70, 76, 79, 0.2)',
                    }}
                    title="Embedded Frame"
                />
                <iframe
                    style={{
                        background: "#FFFFFF",
                        border: "none",
                        borderRadius: "2px",
                        boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)"
                    }}
                    width="550"
                    height="400"
                    src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=bf0b025d-c891-442c-bdf7-9f6ba2be20e1&maxDataAge=3600&theme=light&autoRefresh=true"
                    title="MongoDB Chart"
                ></iframe>
                <iframe
                    style={{
                        background: "#FFFFFF",
                        border: "none",
                        borderRadius: "2px",
                        boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)"
                    }}
                    width="840"
                    height="350"
                    src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=cea82e30-26c5-4ffb-9a21-4770da7e6ee5&maxDataAge=3600&theme=light&autoRefresh=true"
                    title="MongoDB Chart"
                ></iframe>
                <iframe
                    style={{
                        background: "#FFFFFF",
                        border: "none",
                        borderRadius: "2px",
                        boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)"
                    }}
                    width="840"
                    height="350"
                    src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=8819c448-c3d5-4795-8967-cd0d87b3ab3d&maxDataAge=3600&theme=light&autoRefresh=true"
                    title="MongoDB Chart"
                ></iframe>

            </div>

        </div>
    );
}

module.exports = ChartsComponent;

