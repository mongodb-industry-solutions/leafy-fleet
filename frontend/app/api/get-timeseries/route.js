import { NextResponse } from 'next/server';

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

    console.log('Fetching data from:', `http://${process.env.NEXT_PUBLIC_TIMESERIES_GET_SERVICE_URL}/timeseries/all/latest?thread_id=${thread_id}`);

    const response = await fetch(
      `http://${process.env.NEXT_PUBLIC_TIMESERIES_GET_SERVICE_URL}/timeseries/all/latest?thread_id=${thread_id}`,
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
    console.error('Error fetching timeseries data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch timeseries data' },
      { status: 500 }
    );
  }
}
