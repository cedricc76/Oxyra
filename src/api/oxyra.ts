import { API_BASE_URL } from "./base";

export interface OxyraResponse {
  reply: string;
  history: any[];
  intent: string;
  latency: number;
  locations_used: string[];
}

export async function sendMessageToOxyra(
  message: string,
  history: any[] = []
): Promise<OxyraResponse> {
  if (!API_BASE_URL) {
    return {
      reply: "Konfigurasi error: VITE_API_BASE_URL belum diset.",
      history,
      intent: "error",
      latency: 0,
      locations_used: [],
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    const contentType = response.headers.get("content-type") || "";

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(`Server OXYRA error (${response.status}): ${text}`);
    }

    // Kalau server balas HTML (misalnya error page), kasih error jelas
    if (!contentType.includes("application/json")) {
      const text = await response.text().catch(() => "");
      throw new Error(
        `Expected JSON but got ${contentType}. Body: ${text.slice(0, 200)}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("sendMessageToOxyra error:", error);
    return {
      reply: "Maaf, server OXYRA tidak merespons.",
      history,
      intent: "error",
      latency: 0,
      locations_used: [],
    };
  }
}