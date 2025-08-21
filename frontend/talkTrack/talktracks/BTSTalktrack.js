import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function BTSTalktrackSection() {
  return createTalktrackSection({
    heading: "Behind the Scenes",
    content: [
      htmlBodyComponent(
        "Behind the Scenes",
        `
        <div>
          <p><strong>Overview:</strong> Real-time vehicle telemetry analysis, route tracking, and predictive insights are provided by a small set of integrated services:</p>
          <ul>
            <li><strong>MongoDB Atlas:</strong> Centralized timeseries and document storage for telemetry, profiles, and recommendations.</li>
            <li><strong>FastAPI microservices:</strong> Lightweight APIs that ingest telemetry, run agent workflows, and serve the frontend.</li>
            <li><strong>Google Maps API:</strong> Routing, geocoding and map visualization for tracking and geofencing.</li>
            <li><strong>RAG-based AI agent (LangGraph):</strong> Multi-step retrieval and reasoning pipeline that assembles context and generates diagnostic recommendations.</li>
            <li><strong>Voyage AI embeddings:</strong> Text embeddings used for semantic search and similarity-based retrieval.</li>
          </ul>
          <p>These components capture, store, enrich, and analyze telemetry to deliver concise, actionable insights to fleet managers.</p>
        </div>
        `
      ),
      htmlBodyComponent(
        "Architecture Diagram",
        `<img src="/info.png" alt="Logical Architecture" style="max-width: 100%; height: auto;" />`
      ),
    ],
    image: {
      src: "/info.png",
      alt: "Logical Architecture",
    },
  });
}