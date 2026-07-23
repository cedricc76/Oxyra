# api_jatim.py
"""API kecil penyaji data realtime Jawa Timur dari realtime_jatim.csv.
Jalan di VPS. Diakses chatbot lokal (sekarang) & web Vercel (nanti)."""
import csv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CSV_FILE = "data/historical_jatim.csv"
app = FastAPI(title="OXYRA Realtime Jatim API")

# Izinkan akses dari mana saja (chatbot lokal + web Vercel nanti)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                    allow_methods=["*"], allow_headers=["*"])

def baca_csv():
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def terbaru_per_kota(rows):
    hasil = {}
    for r in rows:
        kota = r["kota_diminta"]
        if kota not in hasil or r["waktu_ambil"] > hasil[kota]["waktu_ambil"]:
            hasil[kota] = r
    return list(hasil.values())

@app.get("/")
def root():
    rows = baca_csv()
    return {"status": "ok", "total_baris": len(rows),
            "info": "OXYRA Realtime Jatim API. Endpoint: /terbaru, /kota/{nama}, /semua"}

@app.get("/terbaru")
def terbaru():
    """Data terbaru semua kota."""
    rows = baca_csv()
    data = terbaru_per_kota(rows)
    return {"jumlah_kota": len(data), "data": data}

@app.get("/kota/{nama}")
def kota(nama: str):
    """Data terbaru + riwayat satu kota."""
    rows = baca_csv()
    cocok = [r for r in rows if r["kota_diminta"].lower() == nama.lower()]
    if not cocok:
        return {"status": "tidak_ada", "kota": nama,
                "pesan": f"Data kota '{nama}' tidak ditemukan."}
    cocok.sort(key=lambda r: r["waktu_ambil"])
    return {"kota": nama, "terbaru": cocok[-1],
            "jumlah_riwayat": len(cocok), "riwayat": cocok}

@app.get("/semua")
def semua():
    """Seluruh data mentah."""
    rows = baca_csv()
    return {"jumlah_baris": len(rows), "data": rows}