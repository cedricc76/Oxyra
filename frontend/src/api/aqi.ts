// src/api/aqi.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string || "/api/iqair";

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

// ── AQI agregat Jawa Timur (untuk kartu Dashboard) ─────────────
// Sumber: GET /terbaru (backend meneruskan data VPS yang diperbarui
// tiap 2 jam oleh collector). Nilai kartu = rata-rata AQI 15 kota.
export interface AqiJatim {
  location: string;
  aqi: number;
  kategori: string;
  jumlahKota: number;
  waktuData: string;
}

function kategoriAqi(aqi: number): string {
  if (aqi <= 50) return "Baik";
  if (aqi <= 100) return "Sedang";
  if (aqi <= 150) return "Tidak Sehat bagi Kelompok Sensitif";
  if (aqi <= 200) return "Tidak Sehat";
  if (aqi <= 300) return "Sangat Tidak Sehat";
  return "Berbahaya";
}

export async function getAqiJatim(): Promise<AqiJatim> {
  const response = await fetch(`${API_BASE_URL}/terbaru`);
  if (!response.ok) {
    throw new Error(`Gagal mengambil data Jatim (${response.status})`);
  }
  const json = await response.json();
  const rows: any[] = json.data || [];
  const nilaiAqi = rows
    .map(r => Number(r.aqi_us ?? r.aqi ?? NaN))
    .filter(v => Number.isFinite(v));
  if (nilaiAqi.length === 0) {
    throw new Error("Data AQI Jatim kosong.");
  }
  const rata = Math.round(nilaiAqi.reduce((a, b) => a + b, 0) / nilaiAqi.length);
  const waktu = rows.map(r => String(r.waktu_ambil ?? "")).sort().pop() || "";
  return {
    location: "Jawa Timur",
    aqi: rata,
    kategori: kategoriAqi(rata),
    jumlahKota: nilaiAqi.length,
    waktuData: waktu,
  };
}