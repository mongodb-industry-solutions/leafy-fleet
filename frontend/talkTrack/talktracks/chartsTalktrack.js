import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";


export default function chartsTalktrackSection() {
  return createTalktrackSection({
    heading: "Charts Talktrack",
    content: [
      bodyComponent("Purpose", "This is the demo purpose."),
      htmlBodyComponent(
        "Flexible Data Model",
        `<div>MongoDB's <a href="https://www.mongodb.com/resources/basics/databases/document-databases" target="_blank">document-oriented architecture</a> allows you to store varied data
          (such as <i>timeseries logs, agent profiles, and recommendation outputs</i>)
          in a <strong>single unified format</strong>. This flexibility means you don't have to redesign your database <mark>schema</mark> every time your data requirements evolve.</div>`,
      ),
      bodyComponent(
        "Extra Info",
        "MongoDB's document-oriented architecture allows you to store varied data in a single unified format."
      ),
    ],
  });
}