// src/api/oxyra.ts

const N8N_BASE_URL = import.meta.env.VITE_N8N_BASE_URL as string || "http://localhost:5678";

export interface OxyraResponse {
  reply: string;
  intent: string;
  history?: any[];
  latency?: number;
  locations_used?: string[];
}

export async function sendMessageToOxyra(
  message: string,
  history: any[] = [],
  sessionId: string = "default"
): Promise<OxyraResponse> {
  try {
    const response = await fetch(`${N8N_BASE_URL}/webhook/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        model: "qwen2.5:3b",
      }),
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(`Server error (${response.status}): ${text}`);
    }

    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      const text = await response.text().catch(() => "");
      throw new Error(`Expected JSON but got ${contentType}. Body: ${text.slice(0, 200)}`);
    }

    const data = await response.json();

    return {
      reply: data.reply || "Tidak ada respons.",
      intent: data.intent || "UNKNOWN",
      history: history,
      latency: 0,
      locations_used: [],
    };

  } catch (error) {
    console.error("sendMessageToOxyra error:", error);
    return {
      reply: "Maaf, server OXYRA tidak merespons. Pastikan backend sedang berjalan.",
      intent: "error",
      history,
      latency: 0,
      locations_used: [],
    };
  }
}