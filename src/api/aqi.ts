// src/api/aqi.ts
const N8N_BASE_URL = import.meta.env.VITE_N8N_BASE_URL as string || "http://localhost:5678";

export interface AqiResponse {
  location: string;
  aqi: number;
  interpretation: string;
  pm25: number;
  pm10: number;
  co: number;
  no2: number;
  o3: number;
  so2: number;
}

export async function getAqi(location: string): Promise<AqiResponse> {
  const response = await fetch(
    `${N8N_BASE_URL}/webhook/aqi?location=${encodeURIComponent(location)}`
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`Gagal mengambil data AQI (${response.status}): ${text}`);
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const text = await response.text().catch(() => "");
    throw new Error(`Expected JSON but got ${contentType}. Body: ${text.slice(0, 200)}`);
  }

  return response.json();
}