/**
 * Why MongoDB = WM Talktrack
 * Hope now this filename makes sense.
 */

import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function whyMongoDBTalktrackSection() {
  return createTalktrackSection({
    heading: "Why MongoDB?",
    content: [
      htmlBodyComponent("Flexible Data Model", `<div>MongoDB's <a href="https://www.mongodb.com/resources/basics/databases/document-databases" target="_blank">document-oriented architecture</a> allows you to store varied data 
                (such as <i>timeseries logs, agent profiles, and recommendation outputs</i>) 
                in a <strong>single unified format</strong>. This flexibility means you don’t have to redesign your database <mark>schema</mark> every time your data requirements evolve.</div>`),
      bodyComponent("Scalability and Performance", "MongoDB is designed to scale horizontally, making it capable of handling large volumes of real-time data. This is essential when multiple data sources send timeseries data simultaneously, ensuring high performance under heavy load."),
      bodyComponent(
        "Real-Time Analytics",
        "With powerful aggregation frameworks and change streams, MongoDB supports real-time data analysis and anomaly detection. This enables the system to process incoming timeseries data on the fly and quickly surface critical insights."
      ),
      bodyComponent(
        "Seamless Integration",
        "MongoDB integrates seamlessly with various data sources and platforms, allowing for a more cohesive data ecosystem. This is particularly beneficial for organizations looking to unify their data pipelines and analytics."
      ),
      bodyComponent(
        "Vector Search",
        "MongoDB's vector search capabilities allow for efficient searching and retrieval of high-dimensional data, making it ideal for applications like image and text similarity."
      ),
    ],
  });
}