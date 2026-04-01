// // src/api/aqi.ts
// const N8N_BASE_URL = import.meta.env.VITE_N8N_BASE_URL as string || "http://localhost:5678";

// export interface AqiResponse {
//   location: string;
//   aqi: number;
//   interpretation: string;
//   pm25: number;
//   pm10: number;
//   co: number;
//   no2: number;
//   o3: number;
//   so2: number;
// }

// export async function getAqi(location: string): Promise<AqiResponse> {
//   const response = await fetch(
//     `${N8N_BASE_URL}/webhook/aqi?location=${encodeURIComponent(location)}`
//   );

//   if (!response.ok) {
//     const text = await response.text().catch(() => "");
//     throw new Error(`Gagal mengambil data AQI (${response.status}): ${text}`);
//   }

//   const contentType = response.headers.get("content-type") || "";
//   if (!contentType.includes("application/json")) {
//     const text = await response.text().catch(() => "");
//     throw new Error(`Expected JSON but got ${contentType}. Body: ${text.slice(0, 200)}`);
//   }

//   return response.json();
// }

// src/api/aqi.ts
// Updated: menggunakan FastAPI backend (Ollama + Qwen2.5:3b)

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string || "http://localhost:8000";

export interface AqiResponse {
  location: string;
  aqi: number;
  interpretation: string;
  aqi_label: string;
  pm25: number;
  pm10: number;
  co: number;
  no2: number;
  o3: number;
  so2: number;
}

export async function getAqi(location: string): Promise<AqiResponse> {
  const response = await fetch(
    `${API_BASE_URL}/aqi/${encodeURIComponent(location)}`,
    {
      headers: {
        // Header ini diperlukan karena ngrok memblokir request tanpa header ini
        "ngrok-skip-browser-warning": "true",
      },
    }
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

  const data = await response.json();

  // Map response dari FastAPI ke format AqiResponse
  return {
    location: data.city || location,
    aqi: data.aqi,
    interpretation: data.aqi_label || "",
    aqi_label: data.aqi_label || "",
    pm25: data.pm2_5 || 0,
    pm10: data.pm10 || 0,
    co: data.co || 0,
    no2: data.no2 || 0,
    o3: data.o3 || 0,
    so2: data.so2 || 0,
  };
}

export async function getAqiTrend(location: string, days: number = 7) {
  const response = await fetch(
    `${API_BASE_URL}/trend/${encodeURIComponent(location)}?days=${days}`,
    {
      headers: {
        "ngrok-skip-browser-warning": "true",
      },
    }
  );

  if (!response.ok) throw new Error(`Gagal mengambil tren AQI`);
  return response.json();
}