"use client";

import { useEffect } from "react";
import styles from "./ChartsComponent.module.css";
import InfoCardComponent from "@/components/InfocardComponent/InfocardComponent";
import { useDispatch, useSelector } from "react-redux";
import { useState } from "react";
const ChartsComponent = () => {
  const fleet1Capacity = useSelector((state) => state.User.fleet1Capacity);
  const fleet2Capacity = useSelector((state) => state.User.fleet2Capacity);
  const fleet3Capacity = useSelector((state) => state.User.fleet3Capacity);
  const fleet1Name = useSelector((state) => state.User.fleet1Name);
  const fleet2Name = useSelector((state) => state.User.fleet2Name);
  const fleet3Name = useSelector((state) => state.User.fleet3Name);
  const thread_id = useSelector((state) => state.User.sessionId);

  const [fleet1Cars, setFleet1Cars] = useState([]);
  const [fleet2Cars, setFleet2Cars] = useState([]);
  const [fleet3Cars, setFleet3Cars] = useState([]);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `http://${process.env.NEXT_PUBLIC_AGENT_SERVICE_URL}/timeseries/all/latest?thread_id=${thread_id}`
        );

        if (!res.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await res.json();
        // the data returns a collection of ordered by carID of cars, I want to separate them by the fleet1Capacity, fleet2Capacity+100 and fleet3Capacity+200
        const fleet1 = data.filter((car) => car.car_id <= fleet1Capacity);
        const fleet2 = data.filter(
          (car) =>
            car.car_id > fleet1Capacity && car.car_id <= fleet2Capacity + 100
        );
        const fleet3 = data.filter(
          (car) =>
            car.car_id > fleet2Capacity + 100 &&
            car.car_id <= fleet3Capacity + 200
        );
        // Update state with fleet data
        setFleet1Cars(fleet1);
        setFleet2Cars(fleet2);
        setFleet3Cars(fleet3);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []); // Empty dependency array ensures this runs once when the component mounts

  return (
    <div className={styles.container}>
      <div className={styles.topPart} style={{ flex: 1 }}>
        <InfoCardComponent title={fleet1Name} fleetSize={fleet1Capacity} car={fleet1Cars} />
        <InfoCardComponent title={fleet2Name} fleetSize={fleet2Capacity} car={fleet2Cars} />
        <InfoCardComponent title={fleet3Name} fleetSize={fleet3Capacity} car={fleet3Cars} />
      </div>
      <div className={styles.bottomPart} style={{ flex: 5 }}>
        <iframe
          src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=3bb18da5-6d6a-43d8-aa0d-8924eefc58cd&maxDataAge=3600&theme=light&autoRefresh=true"
          width="500"
          height="400"
          style={{
            background: "#FFFFFF",
            border: "none",
            borderRadius: "2px",
            boxShadow: "0 2px 10px 0 rgba(70, 76, 79, 0.2)",
          }}
          title="My Iframe"
        />

        <iframe
          src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=eae4af4e-6804-4c48-8bde-d06ef567183e&maxDataAge=3600&theme=light&autoRefresh=true"
          width="500"
          height="400"
          style={{
            background: "#FFFFFF",
            border: "none",
            borderRadius: "2px",
            boxShadow: "0 2px 10px 0 rgba(70, 76, 79, 0.2)",
          }}
          title="Embedded Frame"
        />
        <iframe
          style={{
            background: "#FFFFFF",
            border: "none",
            borderRadius: "2px",
            boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)",
          }}
          width="500"
          height="400"
          src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=bf0b025d-c891-442c-bdf7-9f6ba2be20e1&maxDataAge=3600&theme=light&autoRefresh=true"
          title="MongoDB Chart"
        ></iframe>
        <iframe
          style={{
            background: "#FFFFFF",
            border: "none",
            borderRadius: "2px",
            boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)",
          }}
          width="700"
          height="350"
          src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=cea82e30-26c5-4ffb-9a21-4770da7e6ee5&maxDataAge=3600&theme=light&autoRefresh=true"
          title="MongoDB Chart"
        ></iframe>
        <iframe
          style={{
            background: "#FFFFFF",
            border: "none",
            borderRadius: "2px",
            boxShadow: "0 2px 10px 0 rgba(70, 76, 79, .2)",
          }}
          width="700"
          height="350"
          src="https://charts.mongodb.com/charts-jeffn-zsdtj/embed/charts?id=8819c448-c3d5-4795-8967-cd0d87b3ab3d&maxDataAge=3600&theme=light&autoRefresh=true"
          title="MongoDB Chart"
        ></iframe>
      </div>
    </div>
  );
};

module.exports = ChartsComponent;
