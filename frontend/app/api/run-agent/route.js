import { NextResponse } from 'next/server';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const query_reported = searchParams.get('query_reported');
    const thread_id = searchParams.get('thread_id');
    const filters = searchParams.get('filters');
    const preferences = searchParams.get('preferences');

    if (!query_reported || !thread_id) {
      return NextResponse.json(
        { error: 'query_reported and thread_id are required' },
        { status: 400 }
      );
    }

    const url = `http://${process.env.NEXT_PUBLIC_AGENT_SERVICE_URL}/run-agent?query_reported=${encodeURIComponent(
      query_reported
    )}&thread_id=${thread_id}&filters=${encodeURIComponent(
      filters || '[]'
    )}&preferences=${encodeURIComponent(preferences || '[]')}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const text = await response.text();
    
    try {
      // Parse JSON if valid
      const parsedData = JSON.parse(text);
      return NextResponse.json(parsedData);
    } catch (jsonParseError) {
      console.error("Error parsing JSON:", jsonParseError);
      return NextResponse.json(
        { error: "Invalid response format from agent service" },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error calling agent service:', error);
    return NextResponse.json(
      { error: 'Failed to call agent service' },
      { status: 500 }
    );
  }
}
