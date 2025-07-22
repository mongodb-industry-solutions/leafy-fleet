import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function BTSTalktrackSection() {
  return createTalktrackSection({
    heading: "Behind the Scenes",
    content: [
      bodyComponent("Logical Architecture", "This is the demo purpose."),
    ],
    image: {
      src: "./info.png",
      alt: "Logical Architecture",
    }
  });
}