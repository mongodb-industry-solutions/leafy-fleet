import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function chatTalktrackSection() {
  return createTalktrackSection({
    heading: "Instructions and Talk Track",
    content: [
      htmlBodyComponent("How to demo this page", `
        <div>
          <p><strong>Start the app:</strong> Wait for the <mark>Session ID</mark> in the top bar — the simulation and live telemetry start automatically.</p>
          <p><strong>Use the left chat:</strong> Type a question or click a suggested prompt to ask the assistant.</p>
          <p><strong>Assistant:</strong> Has <em>real-time</em> access to simulation data and shows its steps (<strong>Chain of Thought</strong>).</p>
          <p><strong>Answer:</strong> Returns a concise, LLM-powered response with actionable recommendations when available.</p>
          <p><strong>It should look like this:</strong></p>
          <img src="/response_example.png" alt="Chat Example" style="max-width: 100%; height: auto;" />
          <p><strong>Right panel:</strong></p>
          <ul>
            <li><strong>Filters:</strong> Narrow which vehicles are shown by criteria.</li>
            <li><strong>Fleets:</strong> View selected fleet names and capacities.</li>
            <li><strong>Agent Runs:</strong> Inspect tools, data sources, and the agent checkpoint — click the <mark>eye</mark> on a bot response to view documents.</li>
          </ul>
          <p><strong>Example of how it looks:</strong></p>
          <img src="/agent_run_documents_example.png" alt="Agent Run Documents Example" style="max-width: 100%; height: auto;" />
          <p><em>Tip:</em> Apply filters first to get focused, faster responses.</p>
          <p><strong>Note:</strong> Each fleet can contain up to <strong>100 cars</strong> and there can be up to <strong>3 fleets</strong>. IDs are partitioned by fleet: <em>Fleet 1: 0–99</em>, <em>Fleet 2: 100–199</em>, <em>Fleet 3: 200–299</em>. For example, 20 cars in Fleet 1 use IDs <code>0–19</code>, while 20 cars in Fleet 2 use IDs <code>100–119</code>, you <strong>won't </strong> be able to ask about car 121.</strong></p>
        </div>
      `),
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
    ],
  });
}
