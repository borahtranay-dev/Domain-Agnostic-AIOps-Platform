import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { url } = await req.json();

    if (!url || typeof url !== "string") {
      return NextResponse.json({ success: false, error: "Invalid URL provided" }, { status: 400 });
    }

    let targetUrl = url.trim();
    if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
      targetUrl = "https://" + targetUrl;
    }

    // SSRF Prevention: Disallow private IP ranges and cloud metadata endpoints
    try {
      const parsed = new URL(targetUrl);
      const host = parsed.hostname.toLowerCase();
      if (
        host === "localhost" ||
        host === "127.0.0.1" ||
        host === "0.0.0.0" ||
        host.startsWith("192.168.") ||
        host.startsWith("10.") ||
        host.startsWith("172.16.") ||
        host === "169.254.169.254" // AWS/Cloud metadata service IP
      ) {
        return NextResponse.json(
          { success: false, error: "Access to private localhost/intranet addresses is blocked for security." },
          { status: 403 }
        );
      }
    } catch {
      return NextResponse.json({ success: false, error: "Invalid URL structure provided." }, { status: 400 });
    }

    const startTime = Date.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000); // 6s timeout

      const response = await fetch(targetUrl, {
        method: "GET",
        headers: {
          "User-Agent": "AIOps-Health-Monitor/1.0",
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const latencyMs = Date.now() - startTime;

      if (response.ok) {
        return NextResponse.json({
          success: true,
          status: response.status,
          statusText: response.statusText,
          latency: `${latencyMs}ms`,
          healthy: true,
          message: `HTTP ${response.status} OK - Live response in ${latencyMs}ms`,
        });
      } else {
        return NextResponse.json({
          success: true,
          status: response.status,
          statusText: response.statusText,
          latency: `${latencyMs}ms`,
          healthy: false,
          message: `HTTP ${response.status} ${response.statusText} - Site returned error status`,
        });
      }
    } catch (fetchErr: any) {
      const latencyMs = Date.now() - startTime;
      const isTimeout = fetchErr.name === "AbortError";
      return NextResponse.json({
        success: true,
        status: 504,
        latency: `${latencyMs}ms`,
        healthy: false,
        message: isTimeout
          ? `Connection Timed Out after 6s. Target endpoint unreachable.`
          : `Network Unreachable: ${fetchErr.message || "Failed to connect to host"}`,
      });
    }
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message || "Failed to perform health ping" },
      { status: 500 }
    );
  }
}

