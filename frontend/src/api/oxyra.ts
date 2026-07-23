// src/api/oxyra.ts — mendukung dua subsistem: Jawa Timur (real-time) & USA (historis EPA)
// Jatim  -> backend_web.py      (default http://localhost:8000)
// USA    -> backend_web_usa.py  (default http://localhost:8001)

export type Subsystem = "jatim" | "usa";

const JATIM_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || "/api/iqair";
const USA_BASE_URL =
  (import.meta.env.VITE_API_USA_BASE_URL as string | undefined) || "/api/usa";

function baseUrl(subsystem: Subsystem): string {
  return subsystem === "usa" ? USA_BASE_URL : JATIM_BASE_URL;
}

export interface OxyraResponse {
  reply: string;
  intent: string;
  history: any[];
  tools_called?: string[];
  response_ms?: number;
  chart?: any;
}

export async function sendMessageToOxyra(
  message: string,
  history: any[] = [],
  subsystem: Subsystem = "jatim",
  model: string = "llama3.1:8b"
): Promise<OxyraResponse> {
  try {
    const response = await fetch(`${baseUrl(subsystem)}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        model,
      }),
    });

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      throw new Error(`Server error (${response.status}): ${text}`);
    }

    const data = await response.json();

    return {
      reply:        data.reply || "Tidak ada respons.",
      intent:       "chat",
      history:      history,
      tools_called: data.tools_dipakai || [],
      response_ms:  0,
      chart:        data.chart || null,
    };
  } catch (error) {
    console.error("sendMessageToOxyra error:", error);
    const port = subsystem === "usa" ? "8001" : "8000";
    return {
      reply:   `Maaf, server OXYRA (${subsystem === "usa" ? "USA" : "Jawa Timur"}) tidak merespons. Pastikan backend berjalan di port ${port}.`,
      intent:  "error",
      history: history,
    };
  }
}