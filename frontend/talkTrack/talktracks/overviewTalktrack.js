import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function chatTalktrackSection() {
  return createTalktrackSection({
    heading: "Instructions and Talk Track",
    content: [
      htmlBodyComponent(
        "Geospatial Search",
        `<strong>Leafy Fleet</strong> provides powerful geospatial search capabilities for fleet management and vehicle tracking. Query vehicles based on their proximity to geofences or their location within specific areas.<br/><br>
        The <b>Geospatial Search</b> feature utilizes MongoDB's <b> Geospatial Query Operators</b> on vehicle's latest data. <br><br>     
        Once you have located the cars via this search, it showcases fuel levels, engine status, and performance metrics, as well as the complete document model showing telemetry data and vehicle's details (brand, year, maintenance history).<br/>  
        `
      ),
      htmlBodyComponent("How to Demo",[ 
       `<b>Choose search type:</b> Near Geofence or Inside Geofence <br/>`,  
       `<b>Configure: </b>Fleet filters, distance range, and geofences to target.<br/>`,
        `<b>Analyze Results:</b>  
        Review vehicle details including car ID, location coordinates, and operational status: and examine the complete document model showing telemetry data and vehicle metrics`
    ]),
    ],
  });
}