import bodyComponent, { htmlBodyComponent } from "./components/bodyComponent.js";
import {
  createTalktrackSection,
  combineTalktrackSections,
} from "./components/talktrackComponent.js";

/*
Transform this into a builder pattern
The director is PageHeader.jsx which will use the builder function
The builder function will call a collection of talkTrackSections
and return a talktrackDemo function that can be used in the InfoWizard component depending on location of the page.


*/




export function talktrackDemo() {
  return combineTalktrackSections(
    createTalktrackSection({
      heading: "Chat Talktrack",
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
    }),
    createTalktrackSection({
      heading: "RAG Architecture",
      content: [
        bodyComponent("Purpose", "This is the demo purpose."),
        bodyComponent("How to Demo", [
          "Step 1: Do something.",
          "Step 2: Do something else.",
        ]),
        bodyComponent(
          "Extra Info",
          "MongoDB's document-oriented architecture allows you to store varied data in a single unified format."
        ),
      ],
    })
  );
}

export default talktrackDemo;
