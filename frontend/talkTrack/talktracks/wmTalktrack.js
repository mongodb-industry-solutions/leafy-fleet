/**
 * Why MongoDB = WM Talktrack
 * Hope now this filename makes sense.
 */

import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function whyMongoDBTalktrackSection() {
  return createTalktrackSection({
    heading: "Why MongoDB Talktrack",
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
  });
}