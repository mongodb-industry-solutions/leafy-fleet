import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  try {
    const { carId } = params;

    console.log('[API static] Request received for carId:', carId);

    const backendUrl = `http://${process.env.NEXT_PUBLIC_STATIC_SERVICE_URL}/static/${carId}`;
    console.log('[API static] Calling backend:', backendUrl);

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('[API static] Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[API static] Backend error:', errorText);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log('[API static] Backend returned data for car:', carId);

    return NextResponse.json(data);
  } catch (error) {
    console.error('[API static] Error:', error.message);
    return NextResponse.json(
      { error: 'Failed to fetch static car data', details: error.message },
      { status: 500 }
    );
  }
}
