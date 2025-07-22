export function chatbotTalktrackSection() {
  return [
          {
            heading: "Titulo del Demo",
            content: [
              {
                heading: "Demo Purpose",
                body: "Demo description",
              },
              {
                heading: "How to Demo",
                body: [
                  {
                    heading: 'Demo Part 1',
                    body: [
                      'Bullet point 1',
                      'Bullet point 2.'
                    ]
                  },
                  {
                    heading: 'Demo Part 2',
                    body: [
                      'Bullet point 1',
                      'Bullet point 2.',
                      'Bullet point 3'
                    ]
                  },
                  {
                    heading: 'Section 2',
                    body: [
                      'Bullet point 1',
                      'Bullet point 2.',]
                    
                  },
                  {
                    heading: 'Review Planned vs. Actual Cost',
                    body: [
                      'Once the job is under “Completed” status, under Work Orders tab, we’ll be able to see the planned and actual Cost, this will dier wether if our quality rate is other than 100%',
                    ]
                  },

                ],
              },
            ],
          },
          {
            heading: "Behind the Scenes",
            content: [
              {
                heading: "Data Flow",
                body: "",
              },
              {
                image: {
                  src: "./demoOverview.png",
                  alt: "Architecture",
                },
              },
            ],
          },
          {
            heading: "Why MongoDB?",
            content: [
              {
                heading: "Flexible Schema Design",
                body: "Manufacturing environments often deal with highly variable data structures—from machine sensor data to ERP records. MongoDB’s document-oriented design allows data to be stored in JSON-like structures, which can be adapted to capture a wide range of data formats. Unlike traditional relational databases, MongoDB’s schema flexibility means that changes in data requirements, such as adding new sensors or modifying machine attributes, can be easily managed without the need for a rigid data schema.",
              },
              {
                heading: "Real-Time Data Processing",
                body: " MongoDB supports real-time data ingestion through technologies like Kafka change streams and MQTT, making it easy to capture live data from shop floor machines and synchronize with ERP and MES systems. This ability to process streaming data from multiple sources ensures that the UNS provides up-to-date information, supporting timely interventions and data-driven decisions.",
              },
              {
                heading: "Rich Querying and Analytics",
                body: "MongoDB’s aggregation framework and powerful querying capabilities enable in-depth analysis across different data streams. For instance, production teams can cross-reference MES quality metrics with machine sensor data to identify trends and improve quality control processes. Similarly, finance teams can analyze ERP cost data alongside MES output, offering a holistic view of operational efficiency and costs.",
              },
              {
                heading: "Scalability for Growing Operations",
                body: " MongoDB’s distributed architecture allows it to scale horizontally, which is especially valuable in large manufacturing environments where data volumes can grow rapidly. MongoDB clusters can be easily expanded, ensuring the UNS remains responsive even as more machines and production lines are added.",
              },
              {
                heading: "Predictive Maintenance Enablement",
                body: "With MongoDB as a central repository, manufacturers can leverage predictive maintenance strategies by analyzing historical data patterns from machine sensors, detecting anomalies, and predicting maintenance needs. This proactive approach helps reduce machine downtime, optimize maintenance schedules, and ultimately lower operational costs.",
              },
              {
                heading: "High Availability",
                body: " One of the downsites of a UNS is that the central data repository becomes a single point of failure. MongoDB’s replica set guarantees ultra high availability and updates without any downtime.",
              },
            ],
          },
        ];
}

export default chatbotTalktrackSection;
