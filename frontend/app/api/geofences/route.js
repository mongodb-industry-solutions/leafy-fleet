export const dynamic = "force-dynamic";

export async function GET(request) {
  try {
    const url = `http://${process.env.NEXT_PUBLIC_GEOSPATIAL_SERVICE_URL}/geofences`;

    console.log("[DEBUG] Calling geofences API:", url);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (error) {
    console.error("[ERROR] Geofences API error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
