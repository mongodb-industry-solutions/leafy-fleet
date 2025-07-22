import BTSTalktrackSection from "./talktracks/BTSTalktrack.js";
import chartsTalktrackSection from "./talktracks/chartsTalktrack.js";
import chatTalktrackSection from "./talktracks/chatTalktrack.js";
import {
  combineTalktrackSections,
} from "./components/talktrackComponent.js";
import overviewTalktrackSection from "./talktracks/overviewTalktrack.js";
import whyMongoDBTalktrackSection from "./talktracks/wmTalktrack.js";

export function talktrackDemo(talktrackRequirement) {

  if (talktrackRequirement === "/chat") {
    return combineTalktrackSections(
      chatTalktrackSection(),
      BTSTalktrackSection(),
      whyMongoDBTalktrackSection()
    );
  }
  if (talktrackRequirement === "/charts") {
    return combineTalktrackSections(
      chartsTalktrackSection(),
      BTSTalktrackSection(),
      whyMongoDBTalktrackSection()
    );
  }
  if (talktrackRequirement === "/overview") {
    return combineTalktrackSections(
      overviewTalktrackSection(),
      BTSTalktrackSection(),
      whyMongoDBTalktrackSection()
    );
  }
  return combineTalktrackSections(
    BTSTalktrackSection(),
    whyMongoDBTalktrackSection()
  );
}

export default talktrackDemo;
