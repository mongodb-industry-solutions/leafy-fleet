import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function chartsTalktrackSection() {
  return createTalktrackSection({
    heading: "Instructions and Talk Track",
    content: [
      bodyComponent(
        "Solution Overview",
        "The Agentic Framework serves as a versatile AI-driven recommendation assistant capable of comprehending your data, performing a multi-step diagnostic workflow using LangGraph, and generating actionable recommendations. The framework integrates several key technologies. It reads timeseries data from a CSV file or MongoDB (simulating various data inputs), generates text embeddings using the Cohere English V3 model, performs vector searches to identify similar past queries from MongoDB, persists session and run data, and finally generates a diagnostic recommendation. MongoDB stores agent profiles, historical recommendations, timeseries data, session logs, and more. This persistent storage not only logs every step of the diagnostic process for traceability but also enables efficient querying and reusability of past data."
      ),
      htmlBodyComponent("How to Demo", [
        "Choose “New Diagnosis.",
        "Enter a query in the text box (e.g., the sample complaint about a knocking sound).",
        "Click the “Run Agent” button and wait for a few minutes as the agent finishes its run.",
        "The workflow, chain-of-thought output, and the final recommendation are shown in the left column.",
        "In the right column, the documents shown are the records inserted during the current agent run.",
      ]),
    ],
  });
}
