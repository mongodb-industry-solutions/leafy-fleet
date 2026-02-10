export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const body = await request.json();

    const url = `http://${process.env.NEXT_PUBLIC_SESSIONS_SERVICE_URL}/sessions/create`;

    console.log("[API sessions-create] Received request");
    console.log(
      "[API sessions-create] Request body:",
      JSON.stringify(body, null, 2),
    );
    console.log("[API sessions-create] Calling backend:", url);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    console.log(
      "[API sessions-create] Backend response status:",
      response.status,
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[API sessions-create] Backend error response:", errorText);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log(
      "[API sessions-create] Backend response data:",
      JSON.stringify(data, null, 2),
    );

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (error) {
    console.error("[API sessions-create] Error:", error.message);
    console.error("[API sessions-create] Stack:", error.stack);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
