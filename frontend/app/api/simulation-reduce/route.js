export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const url = `http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/simulation/reduce-users`;

    console.log("[DEBUG] Calling simulation reduce-users API:", url);

    const response = await fetch(url, {
      method: "POST",
    });

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
    console.error("[ERROR] Simulation reduce-users API error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
