import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function chatTalktrackSection() {
  return createTalktrackSection({
      heading: "Instructions and Talk Track",
      content: [
        htmlBodyComponent(
          "Solution Overview",
          `The Agentic Framework serves as a versatile AI-driven recommendation assistant 
          capable of comprehending your data, performing a multi-step diagnostic workflow using LangGraph, 
          and generating actionable recommendations. The framework integrates several key technologies. 
          It reads timeseries data from a timeseries collection in MongoDB (simulating various data inputs), 
          generates text embeddings using the the Voyage AI voyage 3.5 embedding model, performs vector searches to 
          identify similar past queries from MongoDB, persists session and run data, and finally 
          generates a diagnostic recommendation. MongoDB stores agent profiles, historical recommendations, 
          timeseries data, and more. This persistent storage not only logs every step of the 
          diagnostic process for traceability but also enables efficient querying and reusability of past data.`
        ),
        htmlBodyComponent("How to Demo", [
          `In the user selecting screen, select either <strong>Frida</strong> to immediately access the chat interface with a preselected fleet configuration
          or select <strong>Kicho</strong> to configure a fleet
          `,
          "Select any filters and ask a question to the bot, either write the question or select one of the preselected questions.",
          "The workflow, chain-of-thought output, and the final recommendation are shown in the right column in the Agent Run Documents section.",
          "In the left column, the answer and a real time chain of thought is displayed.",
        ]),
      ],
    });
}