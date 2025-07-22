export function createTalktrackSection({ heading, content }) {
  return {
    heading,
    content
  };
}

export function combineTalktrackSections(...sections) {
  return sections;
}


export default createTalktrackSection;

