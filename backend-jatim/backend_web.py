# backend_web.py    
"""Backend web lokal OXYRA Jawa Timur — satu pintu untuk frontend.
- POST /chat  : chatbot (pakai Ollama lokal via chat_jatim.chat)
- GET /terbaru, /kota/{nama} : teruskan dari API VPS (untuk grafik)
Jalankan: uvicorn backend_web:app --host 0.0.0.0 --port 8000 --reload"""
import httpx,os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# impor logika chatbot yang sudah ada (jangan tulis ulang)
from chat_jatim import chat as chat_jatim

VPS_API = os.getenv("DATA_API_URL","http://202.155.18.127:8000")    # API data di VPS

app = FastAPI(title="OXYRA Web Backend (lokal)")

# izinkan frontend (Vite biasanya :5173) akses
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                    allow_methods=["*"], allow_headers=["*"])

class ChatReq(BaseModel):
    message: str
    model: str = "llama3.1:8b"

@app.get("/")
def root():
    return {"status": "ok", "info": "OXYRA web backend lokal. POST /chat, GET /terbaru, /kota/{nama}"}

# ── DETEKSI PERMINTAAN GRAFIK (deterministik, bukan via LLM) ──
KOTA_JATIM = [
    "Surabaya", "Gresik", "Mojokerto", "Mojosari", "Jombang",
    "Lamongan", "Tuban", "Bojonegoro", "Madiun", "Malang",
    "Singosari", "Pasuruan", "Bangil", "Probolinggo", "Lumajang",
]
KATA_BANDING = ["banding", "perbandingan", "semua kota", "antar kota",
                "peringkat", "ranking", "tertinggi", "terendah",
                "terburuk", "paling buruk", "paling bersih"]
KATA_TREN = ["tren", "trend", "grafik", "riwayat", "pergerakan",
                "naik turun", "perubahan", "historis"]

def _cari_kota(teks: str):
    teks = teks.lower()
    for k in KOTA_JATIM:
        if k.lower() in teks:
            return k
    return None

def deteksi_grafik(pesan: str):
    """Kembalikan dict chart kalau pesan minta grafik, else None.
    Perbandingan diprioritaskan dulu, baru tren."""
    teks = pesan.lower()
    if any(k in teks for k in KATA_BANDING):
        return chart_areas().get("chart")
    if any(k in teks for k in KATA_TREN):
        kota = _cari_kota(teks) or "Surabaya"   # default Surabaya kalau kota tak disebut
        return chart_trend(kota).get("chart")
    return None

@app.post("/chat")
def chat_endpoint(req: ChatReq):
    """Terima pertanyaan dari frontend, jawab via chatbot Jatim (Ollama lokal).
    Kalau pesan minta tren/perbandingan, sertakan juga data grafik."""
    pesan = (req.message or "").strip()
    if not pesan:
        return {"reply": "Silakan tulis pertanyaan tentang kualitas udara Jawa Timur.",
                "tools_dipakai": [], "chart": None}

    # deteksi grafik dulu — kalau gagal, jangan sampai rusak chat
    chart = None
    try:
        chart = deteksi_grafik(pesan)
    except Exception:
        chart = None

    try:
        hasil = chat_jatim(pesan, model=req.model)
        return {"reply": hasil.get("reply", "Tidak ada respons."),
                "tools_dipakai": hasil.get("tools", []),
                "chart": chart}
    except Exception as e:
        return {"reply": f"Maaf, terjadi kesalahan saat memproses: {e}",
                "tools_dipakai": [], "chart": chart}

# ── Teruskan endpoint data dari VPS (untuk grafik di frontend) ──
@app.get("/terbaru")
def terbaru():
    try:
        r = httpx.get(f"{VPS_API}/terbaru", timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "pesan": str(e)}

@app.get("/kota/{nama}")
def kota(nama: str):
    try:
        r = httpx.get(f"{VPS_API}/kota/{nama}", timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "pesan": str(e)}

# ── ENDPOINT GRAFIK (untuk halaman Charts) ──
def _kategori_level(aqi):
    aqi = int(aqi)
    if aqi <= 50: return 1
    if aqi <= 100: return 2
    if aqi <= 150: return 3
    if aqi <= 200: return 4
    return 5

@app.get("/chart/areas")
def chart_areas(days: int = 1):
    """Bar chart: AQI semua kota Jatim terkini."""
    try:
        r = httpx.get(f"{VPS_API}/terbaru", timeout=20)
        data = r.json().get("data", [])
        data = sorted(data, key=lambda d: int(d["aqi_us"]), reverse=True)
        return {"chart": {
            "chart_type": "bar",
            "title": "Perbandingan AQI Kota Jawa Timur (Terkini)",
            "x_key": "kota", "y_keys": ["avg_aqi"], "y_labels": ["AQI"],
            "colors": ["#3b82f6"],
            "data": [{"kota": d["kota_diminta"], "avg_aqi": int(d["aqi_us"])} for d in data],
            "description": "AQI terkini tiap kota Jawa Timur, diurutkan dari tertinggi. Warna sesuai kategori AQI."
        }}
    except Exception as e:
        return {"chart": None, "error": str(e)}

@app.get("/chart/trend/{kota}")
def chart_trend(kota: str, days: int = 7):
    """Line chart: tren AQI satu kota dari riwayat."""
    try:
        r = httpx.get(f"{VPS_API}/kota/{kota}", timeout=20)
        j = r.json()
        riwayat = j.get("riwayat", [])
        if not riwayat:
            return {"chart": None}
        # Hormati parameter days: data tiap 2 jam = 12 titik per hari.
        # Riwayat berurutan naik, jadi ambil potongan terakhir saja.
        riwayat = riwayat[-(max(1, int(days)) * 12):]
        return {"chart": {
            "chart_type": "line",
            "title": f"Tren AQI {kota} ({days} hari terakhir)",
            "x_key": "waktu", "y_keys": ["aqi"], "y_labels": ["AQI"],
            "colors": ["#0ea5e9"],
            "data": [{"waktu": rr["waktu_ambil"][5:16], "aqi": int(rr["aqi_us"])} for rr in riwayat],
            "description": f"Tren kualitas udara {kota} dari waktu ke waktu (data tiap 2 jam)."
        }}
    except Exception as e:
        return {"chart": None, "error": str(e)}

@app.get("/chart/hourly/{kota}")
def chart_hourly(kota: str):
    """Heatmap: pola AQI per jam (level 1-5)."""
    try:
        r = httpx.get(f"{VPS_API}/kota/{kota}", timeout=20)
        j = r.json()
        riwayat = j.get("riwayat", [])
        if not riwayat:
            return {"chart": None}
        return {"chart": {
            "chart_type": "heatmap",
            "title": f"Pola AQI per Waktu — {kota}",
            "x_key": "jam", "y_keys": ["aqi"], "y_labels": ["AQI"],
            "colors": ["#3b82f6"],
            "data": [{"jam": rr["waktu_ambil"][11:16], "aqi": _kategori_level(rr["aqi_us"])} for rr in riwayat],
            "description": f"Pola kualitas udara {kota} per waktu pengambilan (level 1=Baik s/d 5=Sangat Tidak Sehat)."
        }}
    except Exception as e:
        return {"chart": None, "error": str(e)}
    
@app.get("/semua")
def semua():
    try:
        r = httpx.get(f"{VPS_API}/semua", timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "pesan": str(e)}