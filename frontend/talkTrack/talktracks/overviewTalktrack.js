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
      htmlBodyComponent("How to demo this page", [
        `<b>Choose search type:</b> Near to geofence to search for vehicles closest to the center of a specific geofence center point, ordered by distance or Inside Geofence which finds vehicles within a specific prebuilt geofence boundary.<br/>`,
        `<b>If selected "Near to geofence": </b>configure the circular radius where the search will be conducted, you can leave the default radius as is. If there is a car that is closer than the minimum distance, it will not be shown in the results of the search.<br/>`,
         `<b>Configure the filters: </b>If no fleets are selected, vehicles from all 3 fleets will be included in the search. You must select at least 1 Geofence to make the search, and only vehicles from the selected geofence will be shown in the results below.<br/>`,
        `<b>Real time code:</b> The code shown just below the filters is the actual query made to MongoDB to search.<br/>`,
        `<b>Click "Search":</b> This will trigger the geospatial search and display results below the code block.<br/>`,
        `<b>Analyze Results:</b>  
        Review vehicle details shown below the code block including car ID, location coordinates, and operational status: and examine the complete document model showing telemetry data and vehicle metrics`,
      ]),
    ],
  });
}
