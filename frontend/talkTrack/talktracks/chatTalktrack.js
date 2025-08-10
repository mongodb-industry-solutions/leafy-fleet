import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function chatTalktrackSection() {
  return createTalktrackSection({
    heading: "Instructions and Talk Track",
    content: [
      htmlBodyComponent(
        "Solution Overview",
        `<strong>Leafy Fleet</strong> serves as a versatile <b>AI-driven recommendation assistant</b> capable of comprehending your data, performing a <b>multi-step diagnostic workflow</b> using <b>LangGraph</b>, and generating actionable recommendations made for fleet manager to be able to focus on monitoring their fleet's health and performance instead of searching for insights.<br/><br/>
        <b>Key technologies integrated:</b>
        <ul>
          <li>Reads timeseries data from a <b>MongoDB timeseries collection</b> (simulating various data inputs)</li>
          <li>Generates text embeddings using the <b>Voyage AI voyage 3.5 embedding model</b></li>
          <li>Performs <b>vector searches</b> to identify similar past queries from MongoDB</li>
          <li>Persists session and run data</li>
          <li>Generates a <b>diagnostic recommendation</b></li>
        </ul>
        <b>MongoDB</b> stores agent profiles, historical recommendations, timeseries data, and more.<br/>
        This persistent storage not only logs every step of the diagnostic process for <b>traceability</b> but also enables efficient querying and reusability of past data.`
      ),
      htmlBodyComponent("How to Demo", [
        `In the user selecting screen, select either <strong>Frida</strong> to immediately access the chat interface with a preselected fleet configuration,
        or select <strong>Kicho</strong> to configure a fleet.`,
        "<b>Select any filters</b> and ask a question to the bot, either write the question or select one of the preselected questions.",
        "The workflow, <b>chain-of-thought output</b>, and the <b>final recommendation</b> are shown in the right column in the <b>Agent Run Documents</b> section.",
        "In the left column, the answer and a <b>real time chain of thought</b> is displayed.",
      ]),
    ],
  });
}