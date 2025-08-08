import bodyComponent, { htmlBodyComponent } from "../components/bodyComponent";
import createTalktrackSection from "../components/talktrackComponent.js.js";


export default function BTSTalktrackSection(image) {
  return createTalktrackSection({
    heading: "Behind the Scenes",
    content: [
      htmlBodyComponent(
        "Architecture Diagram",
        `<img src="https://raw.githubusercontent.com/mongodb-industry-solutions/leafy-fleet/refs/heads/main/architecture/logical.png?token=GHSAT0AAAAAADF2RAIUVWAEERY6GSLRDK7C2EWKR4Q" alt="Logical Architecture" style="max-width: 100%; height: auto;" />`
      ),
    ],
    image: {
      src: "https://raw.githubusercontent.com/mongodb-industry-solutions/leafy-fleet/refs/heads/main/architecture/logical.png?token=GHSAT0AAAAAADF2RAIUVWAEERY6GSLRDK7C2EWKR4Q",
      alt: "Logical Architecture",
    },
  });
}