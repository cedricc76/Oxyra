# Collector_jatim.py
"""Collector real-time IQAir untuk 16 kota Jawa Timur.
Ambil tiap jam (skip dini hari 01-04 untuk hemat kuota).
Simpan ke realtime_jatim.csv. Muat kuota Community 10.000/bulan (9.600 terpakai)."""
import httpx, time, csv, os
from datetime import datetime, timedelta

API_KEY = os.getenv("IQAIR_API_KEY", "")
os.makedirs("data", exist_ok=True)
URL = "https://api.airvisual.com/v2/nearest_city"
CSV_FILE = "data/historical_jatim.csv"
JEDA = 15          # detik antar kota (hormati rate limit ~5/menit)
JAM_SKIP = set()   # tidak ada jam yang diskip

KOTA_JATIM = {
    "Surabaya": (-7.2575, 112.7521),
    "Malang": (-7.9666, 112.6326),
    "Kediri": (-7.8480, 112.0178),
    "Madiun": (-7.6298, 111.5239),
    "Gresik": (-7.1561, 112.6531),
    "Mojokerto": (-7.4722, 112.4336),
    "Pasuruan": (-7.6453, 112.9075),
    "Probolinggo": (-7.7543, 113.2159),
    "Jombang": (-7.5460, 112.2330),
    "Lumajang": (-8.1335, 113.2240),
    "Bojonegoro": (-7.1502, 111.8817),
    "Bangil": (-7.5990, 112.7810),
    "Singosari": (-7.8920, 112.6650),
    "Mojosari": (-7.5916, 112.5640),
    "Lamongan": (-7.1167, 112.4167),
    "Tuban": (-6.8976, 112.0648),
}

KOLOM = ["waktu_ambil", "kota_diminta", "kota_terdeteksi", "provinsi",
            "aqi_us", "polutan_dominan_us", "aqi_cn", "polutan_dominan_cn",
            "suhu_c", "kelembaban", "tekanan", "angin_ms", "waktu_data"]

def ambil_kota(kota, lat, lon):
    """Ambil data 1 kota. Return dict atau None kalau gagal/tidak valid."""
    try:
        r = httpx.get(URL, params={"lat": lat, "lon": lon, "key": API_KEY}, timeout=15)
        j = r.json()
        if j.get("status") != "success":
            pesan = j.get("data", {}).get("message", j.get("status"))
            print(f"    [GAGAL] {kota}: {pesan}")
            return None
        d = j["data"]
        pol = d["current"]["pollution"]
        cua = d["current"].get("weather", {})
        aqi = pol.get("aqius")
        if not aqi or aqi <= 0:   # AQI 0/kosong = tidak valid
            print(f"    [SKIP]  {kota}: AQI tidak valid ({aqi})")
            return None
        return {
            "waktu_ambil": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "kota_diminta": kota,
            "kota_terdeteksi": d.get("city"),
            "provinsi": d.get("state"),
            "aqi_us": aqi,
            "polutan_dominan_us": pol.get("mainus"),
            "aqi_cn": pol.get("aqicn"),
            "polutan_dominan_cn": pol.get("maincn"),
            "suhu_c": cua.get("tp"),
            "kelembaban": cua.get("hu"),
            "tekanan": cua.get("pr"),
            "angin_ms": cua.get("ws"),
            "waktu_data": pol.get("ts"),
        }
    except Exception as e:
        print(f"    [ERROR] {kota}: {e}")
        return None

def satu_putaran():
    """Ambil semua kota sekali putaran. Return jumlah berhasil."""
    jam = datetime.now().hour
    if jam in JAM_SKIP:
        print(f"Jam {jam:02d}:00 termasuk jam skip, lewati putaran ini.")
        return 0
    print(f"\n=== Putaran {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    baru = not os.path.exists(CSV_FILE)
    berhasil = 0
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLOM)
        if baru:
            w.writeheader()
        for kota, (lat, lon) in KOTA_JATIM.items():
            data = ambil_kota(kota, lat, lon)
            if data:
                w.writerow(data)
                f.flush()
                print(f"    [OK]    {kota:12} -> {data['kota_terdeteksi']}, AQI {data['aqi_us']} ({data['polutan_dominan_us']})")
                berhasil += 1
            time.sleep(JEDA)
    print(f"=== Selesai: {berhasil}/{len(KOTA_JATIM)} kota tersimpan ===")
    return berhasil

def detik_ke_slot_berikut():
    """Detik sampai jam genap berikutnya menit 00 (00,02,...,22)."""
    now = datetime.now()
    jam_berikut = (now.hour // 2 + 1) * 2
    if jam_berikut >= 24:
        target = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        target = now.replace(hour=jam_berikut, minute=0, second=0, microsecond=0)
    return (target - now).total_seconds()

if __name__ == "__main__":
    while True:
        tunggu = detik_ke_slot_berikut()
        print(f"Menunggu {tunggu/60:.0f} menit sampai slot berikutnya...", flush=True)
        time.sleep(tunggu)
        satu_putaran()