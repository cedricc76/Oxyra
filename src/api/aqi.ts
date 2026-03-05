// src/api/aqi.ts
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
    const res = await fetch(`http://127.0.0.1:8000/aqi/${location}`);

    if (!res.ok) {
    throw new Error("Gagal mengambil data AQI");
    }

    return res.json();
}
