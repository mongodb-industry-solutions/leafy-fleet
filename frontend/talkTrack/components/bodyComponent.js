export function bodyComponent(heading, body, isHTML = false) {
  return {
    heading,
    body,
    isHTML,
  };
}

export function htmlBodyComponent(heading, htmlBody) {
  return bodyComponent(heading, htmlBody, true);
}

export default bodyComponent;