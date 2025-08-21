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
      htmlBodyComponent(
        "Flexible Data Model",
        `<div>
          <b>MongoDB's</b> <a href="https://www.mongodb.com/resources/basics/databases/document-databases" target="_blank">document-oriented architecture</a> allows you to store varied data 
          (such as <i>timeseries logs, agent profiles, and recommendation outputs</i>) 
          in a <strong>single unified format</strong>.<br/><br/>
          <ul>
            <li>This flexibility means you don’t have to redesign your database <mark>schema</mark> every time your data requirements evolve.</li>
            <li>Store structured, semi-structured, and unstructured data together.</li>
          </ul>
        </div>`
      ),
      htmlBodyComponent(
        "Scalability and Performance",
        `<b>MongoDB</b> is designed to <b>scale horizontally</b>, making it capable of handling large volumes of real-time data.<br/>
        <ul>
          <li>Essential for multiple data sources sending timeseries data simultaneously.</li>
          <li>Ensures <b>high performance</b> under heavy load.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "Real-Time Analytics",
        `With powerful <b>aggregation frameworks</b> and <b>change streams</b>, MongoDB supports real-time data analysis and anomaly detection.<br/>
        <ul>
          <li>Process incoming timeseries data on the fly.</li>
          <li>Quickly surface critical insights.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "Seamless Integration",
        `<b>MongoDB</b> integrates seamlessly with various data sources and platforms, allowing for a more cohesive data ecosystem.<br/>
        <ul>
          <li>Unify your data pipelines and analytics.</li>
          <li>Accelerate development with a rich ecosystem of connectors and tools.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "Vector Search",
        `<b>MongoDB's vector search</b> capabilities allow for efficient searching and retrieval of high-dimensional data.<br/>
        <ul>
          <li>Ideal for applications like <b>image and text similarity</b>.</li>
          <li>Enables advanced AI and ML use cases.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "Geospatial Queries",
        `<b>MongoDB's geospatial queries</b> allow for efficient location-based data retrieval and analysis.<br/>
        <ul>
          <li>Perfect for fleet management, logistics, and mapping applications.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "RAG (Retrieval-Augmented Generation)",
        `<b>MongoDB's Document model</b> allows for efficient storage and retrieval of large documents—structured, semi-structured, and unstructured.<br/>
        <ul>
          <li>Ideal for <b>RAG applications</b> and generative AI workflows.</li>
        </ul>`
      ),
      htmlBodyComponent(
        "Time Series Collections",
        `<b>MongoDB's time series collections</b> are optimized for storing and querying time series data.<br/>
        <ul>
          <li>Enables efficient implementation of near real-time analytics.</li>
          <li>Reduces storage costs and improves query performance.</li>
        </ul>`
      ),
    ],
  });
}