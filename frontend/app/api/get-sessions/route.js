import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    console.log('POST /api/get-sessions - Starting request');
    
    const body = await request.json();
    console.log('Request body:', JSON.stringify(body, null, 2));
    
    // Validate required fields
    if (!body.vehicle_fleet) {
      console.log('Validation failed: vehicle_fleet is missing');
      return NextResponse.json(
        { error: 'vehicle_fleet is required' },
        { status: 400 }
      );
    }

    const serviceUrl = process.env.NEXT_PUBLIC_SESSIONS_SERVICE_URL;
    console.log('Sessions service URL:', serviceUrl);
    
    if (!serviceUrl) {
      console.error('NEXT_PUBLIC_SESSIONS_SERVICE_URL environment variable is not set');
      return NextResponse.json(
        { error: 'Sessions service URL not configured' },
        { status: 500 }
      );
    }

    const fullUrl = `http://${serviceUrl}/sessions/create`;
    console.log('Making request to:', fullUrl);

    const response = await fetch(fullUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const data = await response.json();
    console.log('Response data:', JSON.stringify(data, null, 2));
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in POST /api/get-sessions:', error);
    console.error('Error stack:', error.stack);
    return NextResponse.json(
      { 
        error: 'Failed to create session',
        details: error.message,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

// Optional: Add GET method if you need to retrieve sessions
export async function GET(request) {
  try {
    console.log('GET /api/get-sessions - Starting request');
    
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');
    console.log('Session ID from query:', sessionId);
    
    const serviceUrl = process.env.NEXT_PUBLIC_SESSIONS_SERVICE_URL;
    console.log('Sessions service URL:', serviceUrl);
    
    if (!serviceUrl) {
      console.error('NEXT_PUBLIC_SESSIONS_SERVICE_URL environment variable is not set');
      return NextResponse.json(
        { error: 'Sessions service URL not configured' },
        { status: 500 }
      );
    }

    let url = `http://${serviceUrl}/sessions`;
    if (sessionId) {
      url += `/${sessionId}`;
    }
    console.log('Making request to:', url);

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const data = await response.json();
    console.log('Response data:', JSON.stringify(data, null, 2));
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in GET /api/get-sessions:', error);
    console.error('Error stack:', error.stack);
    return NextResponse.json(
      { 
        error: 'Failed to fetch sessions',
        details: error.message,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
