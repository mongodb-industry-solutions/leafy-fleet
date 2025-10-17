export const dynamic = 'force-dynamic';

export async function POST(request) {
  try {
    const { searchParams } = new URL(request.url);
    const vehicleCount = searchParams.get('vehicleCount') || '300';

    const url = `http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/simulation/start/${vehicleCount}`;

    console.log('[DEBUG] Calling simulation start API:', url);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Check if it's the specific "already running" error
      if (response.status === 400) {
        const errorData = await response.json();
        if (errorData.detail === "Simulation is already running") {
          // Return success to avoid logging error
          return new Response(JSON.stringify({ message: 'Simulation already running' }), {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
            },
          });
        }
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('[ERROR] Simulation start API error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
