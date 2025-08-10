import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";

export default function BTSTalktrackSection() {
  return createTalktrackSection({
    heading: "Behind the Scenes",
    content: [
      htmlBodyComponent(
        "Architecture Diagram",
        `<img src="/info.png" alt="Logical Architecture" style="max-width: 100%; height: auto;" />`
      ),
    ],
    image: {
      src: "/info.png",
      alt: "Logical Architecture",
    },
  });
}