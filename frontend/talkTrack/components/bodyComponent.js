export function bodyComponent(heading, body, isHTML = false) {
  return {
    heading,
    body,
    isHTML,
  };
}

export function htmlBodyComponent(heading, htmlBody) {
  const formattedBody = Array.isArray(htmlBody)
    ? `<ul>${htmlBody.map((point) => `<li>${point}</li>`).join("")}</ul>` // Render as list
    : `<p>${htmlBody}</p>`; // Render as paragraph

  return bodyComponent(heading, formattedBody, true);
}

export default bodyComponent;