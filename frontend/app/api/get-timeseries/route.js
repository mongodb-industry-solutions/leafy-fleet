import { NextResponse } from "next/server";
export const dynamic = "force-dynamic";

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const thread_id = searchParams.get("thread_id");

    console.log(
      "[API get-timeseries] Request received for thread_id:",
      thread_id,
    );

    if (!thread_id) {
      console.log("[API get-timeseries] Missing thread_id parameter");
      return NextResponse.json(
        { error: "thread_id is required" },
        { status: 400 },
      );
    }

    const backendUrl = `http://${process.env.NEXT_PUBLIC_TIMESERIES_GET_SERVICE_URL}/timeseries/all/latest?thread_id=${thread_id}`;
    console.log("[API get-timeseries] Calling backend:", backendUrl);

    const response = await fetch(backendUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log(
      "[API get-timeseries] Backend response status:",
      response.status,
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[API get-timeseries] Backend error:", errorText);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log("[API get-timeseries] Backend returned data:", {
      isArray: Array.isArray(data),
      length: data?.length,
      firstItem: data?.[0],
    });

    return NextResponse.json(data);
  } catch (error) {
    console.error("[API get-timeseries] Error:", error.message);
    return NextResponse.json(
      { error: "Failed to fetch timeseries data", details: error.message },
      { status: 500 },
    );
  }
}
