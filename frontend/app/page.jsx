"use client";

import { H1, H3, Body, Description, Link } from "@leafygreen-ui/typography";
import Card from "@leafygreen-ui/card";
import SideNavigation from "@/components/SideNav/SideNav";
import Button from "@leafygreen-ui/button";
import styles from "./page.module.css";

export default function HomePage() {


  return (
    <div>
      <SideNavigation />

      <div className={styles.body}>
        <H1 className={styles.pageTitle}>Welcome to the Leafy Fleet Demo!</H1>
        <Button className={styles.startButton}  style={{ background: "#00ED64" }} onClick={() => {
          window.location.href = "/chat";
        }}>
          Go to demo!
        </Button>

        <img
          src="/info.png"
          className={styles.architectureImage}
          alt="Flow of the demo"
        ></img>

        <H3 className={styles.compTitle}>Check out our related resources!</H3>

        <div className={styles.container}>
          <Card className={styles.card}>
            <a
              className={styles.title}
              href="https://www.mongodb.com/resources/solutions/use-cases/generative-ai-predictive-maintenance-applications"
            >
              <img src="/read.png" className={styles.image} alt="Retail"></img>
              <H3 className={styles.title}>White Paper</H3>
            </a>
            <Description className={styles.description}>
              {" "}
              Learn more about using RAG AI Agents to improve fleet managers
              with MongoDB.
            </Description>

            <Link
              href="https://www.mongodb.com/resources/solutions/use-cases/generative-ai-predictive-maintenance-applications"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.button}
            >
              Read the paper
            </Link>
          </Card>

          <Card className={styles.card}>
            <a
              className={styles.title}
              href="https://github.com/mongodb-industry-solutions/leafy-fleet"
            >
              <img
                src="/github.png"
                className={styles.image}
                alt="Insurance"
              ></img>
              <H3 className={styles.title}>Github Repo</H3>
            </a>
            <Description className={styles.description}>
              {" "}
              Follow the step-by-step guide and play around with the demo
              yourself.
            </Description>
            <Link
              href="https://github.com/mongodb-industry-solutions/leafy-fleet"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.button}
            >
              Try the Demo
            </Link>
          </Card>

          <Card className={styles.card}>
            <a
              className={styles.title}
              href="https://www.youtube.com/watch?v=YwTWpUl3QS8"
            >
              <img
                src="/youtube.png"
                className={styles.image}
                alt="Insurance"
              ></img>
              <H3 className={styles.title}>YouTube Video</H3>
            </a>
            <Description className={styles.description}>
              {" "}
              Explore how MongoDB can be leveraged to create an efficient Fleet
              Manager Software.
            </Description>
            <Link
              href="https://www.youtube.com/watch?v=YwTWpUl3QS8"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.button}
            >
              Watch the Video
            </Link>
          </Card>
        </div>
      </div>
    </div>
  );
}
