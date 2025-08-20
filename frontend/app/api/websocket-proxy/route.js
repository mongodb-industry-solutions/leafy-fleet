import { NextResponse } from 'next/server';

// This is a polling-based alternative to WebSocket
// For true WebSocket support, you might need to use a separate server or Next.js custom server
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const thread_id = searchParams.get('thread_id');

    if (!thread_id) {
      return NextResponse.json(
        { error: 'thread_id is required' },
        { status: 400 }
      );
    }

    // This would be a polling endpoint to get latest thoughts/updates
    // You might need to implement this differently based on your backend
    const response = await fetch(
      `http://${process.env.NEXT_PUBLIC_AGENT_SERVICE_URL}/get-latest-thoughts?thread_id=${thread_id}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting latest thoughts:', error);
    return NextResponse.json(
      { error: 'Failed to get latest thoughts' },
      { status: 500 }
    );
  }
}
