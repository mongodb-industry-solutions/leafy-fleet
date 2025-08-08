import BTSTalktrackSection from "./talktracks/BTSTalktrack.js";
import chartsTalktrackSection from "./talktracks/chartsTalktrack.js";
import chatTalktrackSection from "./talktracks/chatTalktrack.js";
import {
  combineTalktrackSections,
} from "./components/talktrackComponent.js";
import overviewTalktrackSection from "./talktracks/overviewTalktrack.js";
import whyMongoDBTalktrackSection from "./talktracks/wmTalktrack.js";
import image from "../public/Arquitecture.png";

export function talktrackDemo(talktrackRequirement) {

  if (talktrackRequirement === "/chat") {
    return combineTalktrackSections(
      chatTalktrackSection(),
      BTSTalktrackSection(image),
      whyMongoDBTalktrackSection()
    );
  }
  if (talktrackRequirement === "/charts") {
    return combineTalktrackSections(
      chartsTalktrackSection(),
      BTSTalktrackSection(image),
      whyMongoDBTalktrackSection()
    );
  }
  if (talktrackRequirement === "/overview") {
    return combineTalktrackSections(
      overviewTalktrackSection(),
      BTSTalktrackSection(image),
      whyMongoDBTalktrackSection()
    );
  }
  return combineTalktrackSections(
    BTSTalktrackSection(image),
    whyMongoDBTalktrackSection()
  );
}

export default talktrackDemo;
