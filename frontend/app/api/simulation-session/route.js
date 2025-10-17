export const dynamic = 'force-dynamic';

export async function POST(request) {
  try {
    const body = await request.json();

    const url = `http://${process.env.NEXT_PUBLIC_SIMULATION_SERVICE_URL}/sessions`;

    console.log('[DEBUG] Calling simulation session API:', url);
    console.log('[DEBUG] Request body:', body);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Simulation service error: ${errorData.detail || response.status}`);
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('[ERROR] Simulation session API error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
