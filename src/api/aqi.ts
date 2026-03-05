// // src/api/aqi.ts
// export interface AqiResponse {
//     location: string;
//     aqi: number;
//     interpretation: string;
//     pm25: number;
//     pm10: number;
//     co: number;
//     no2: number;
//     o3: number;
//     so2: number;
// }

// export async function getAqi(location: string): Promise<AqiResponse> {
//     const res = await fetch(`http://127.0.0.1:8000/aqi/${location}`);

//     if (!res.ok) {
//     throw new Error("Gagal mengambil data AQI");
//     }

//     return res.json();
// }

import { API_BASE_URL } from "./base";

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
  if (!API_BASE_URL) throw new Error("VITE_API_BASE_URL belum diset");

  const url = `${API_BASE_URL}/aqi/${encodeURIComponent(location)}`;
  const res = await fetch(url);

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Gagal mengambil data AQI (${res.status}): ${text}`);
  }

  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `Expected JSON but got ${contentType}. Body: ${text.slice(0, 200)}`
    );
  }

  return res.json();
}