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
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) {
      throw new Error("Server OXYRA error");
    }

    return await response.json();
  } catch (error) {
    return {
      reply: "Maaf, server OXYRA tidak merespons.",
      history,
      intent: "error",
      latency: 0,
      locations_used: [],
    };
  }
}
