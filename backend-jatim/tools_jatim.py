# tools_jatim.py
"""Tools data real-time Jawa Timur — baca dari API VPS.
Dipakai chat engine untuk menjawab pertanyaan kualitas udara Jatim terkini.

Saran kesehatan (_saran) mengikuti cautionary statements resmi US EPA per kategori AQI:
- EPA Technical Assistance Document for the Reporting of Daily Air Quality (AQI), Mei 2024,
    Tabel 5 (Pollutant-Specific Sub-indices and Cautionary Statements) & Tabel 4 (Sensitive Groups).
- AirNow.gov "AQI Basics" (https://www.airnow.gov/aqi/aqi-basics/).
Difokuskan ke PM2.5 karena PM2.5 adalah polutan dominan pada mayoritas pembacaan di Jawa Timur.
"""
import httpx
import os
API_BASE = os.getenv("DATA_API_URL","API_BASE_URL")   # API VPS (nanti ganti ke domain kalau ada))

POLUTAN = {"p2":"PM2.5","p1":"PM10","o3":"Ozon (O3)","n2":"NO2","s2":"SO2","co":"CO"}

def _kategori(aqi):
    aqi = int(aqi)
    if aqi <= 50: return "Baik"
    if aqi <= 100: return "Sedang"
    if aqi <= 150: return "Tidak Sehat bagi Kelompok Sensitif"
    if aqi <= 200: return "Tidak Sehat"
    if aqi <= 300: return "Sangat Tidak Sehat"
    return "Berbahaya"

def _saran(aqi):
    """Arahan kehati-hatian deterministik per kategori AQI (parafrase cautionary
    statement resmi US EPA). Ini PATOKAN untuk LLM, bukan kalimat jadi — LLM
    merangkainya jadi bahasa awam yang luwes. Fokus PM2.5 (polutan dominan Jatim)."""
    aqi = int(aqi)
    if aqi <= 50:
        return "aman untuk semua orang beraktivitas di luar"
    if aqi <= 100:
        # EPA: sedang; kelompok yang tidak biasa sensitif pertimbangkan kurangi aktivitas berat.
        # Jika mendekati 100, perlakukan lebih hati-hati (dekat ambang tidak sehat).
        if aqi >= 90:
            return ("umumnya masih dapat diterima, TETAPI mendekati ambang tidak sehat; "
                    "kelompok sensitif (anak, lansia, penderita asma/gangguan pernapasan) "
                    "sebaiknya membatasi aktivitas luar yang berat atau berkepanjangan")
        return ("umumnya dapat diterima; sebagian kecil orang yang sangat sensitif "
                "sebaiknya mempertimbangkan mengurangi aktivitas luar yang berat")
    if aqi <= 150:
        return ("tidak sehat bagi kelompok sensitif; penderita penyakit jantung/paru, asma, "
                "lansia, dan anak-anak sebaiknya mengurangi aktivitas luar yang berat atau "
                "berkepanjangan dan mempertimbangkan memakai masker")
    if aqi <= 200:
        return ("tidak sehat; semua orang sebaiknya mengurangi aktivitas luar yang berat, "
                "dan kelompok sensitif menghindari aktivitas luar serta memakai masker")
    if aqi <= 300:
        return ("sangat tidak sehat; semua orang sebaiknya menghindari aktivitas luar, "
                "kelompok sensitif tetap di dalam ruangan")
    return ("berbahaya; seluruh warga harus menghindari semua aktivitas luar ruangan")

def _fmt(d):
    aqi = d["aqi_us"]
    pol = POLUTAN.get(d["polutan_dominan_us"], d["polutan_dominan_us"])
    return (f"{d['kota_diminta']}: AQI {aqi} ({_kategori(aqi)}), "
            f"polutan dominan {pol}, suhu {d['suhu_c']}°C, kelembaban {d['kelembaban']}%. "
            f"SARAN RESMI (WAJIB diikuti, jangan lebih optimis): {_saran(aqi)}")

def _ambil(endpoint):
    """Panggil API VPS. Return dict atau None kalau gagal."""
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", timeout=15)
        return r.json()
    except Exception as e:
        return {"status": "error", "pesan": str(e)}

def kondisi_semua_kota():
    """Kondisi terkini semua kota Jawa Timur."""
    j = _ambil("/terbaru")
    if not j or "data" not in j or not j["data"]:
        return {"status": "error", "pesan": "Data tidak tersedia dari server."}
    baris = [_fmt(d) for d in j["data"]]
    return {"status": "ok", "ringkas": "Kondisi terkini kualitas udara Jawa Timur:\n" + "\n".join(baris)}

def kondisi_kota(nama):
    """Kondisi terkini satu kota."""
    j = _ambil(f"/kota/{nama}")
    if not j or j.get("status") == "tidak_ada" or "terbaru" not in j:
        return {"status": "error", "pesan": f"Data kota '{nama}' tidak ditemukan."}
    d = j["terbaru"]
    return {"status": "ok", "ringkas": f"Kondisi {nama}: " + _fmt(d),
            "waktu": d.get("waktu_ambil")}

def peringkat_kota(urutan="terburuk"):
    """Peringkat kota berdasar AQI (terburuk/terbaik)."""
    j = _ambil("/terbaru")
    if not j or "data" not in j or not j["data"]:
        return {"status": "error", "pesan": "Data tidak tersedia."}
    terburuk = urutan != "terbaik"
    data = sorted(j["data"], key=lambda d: int(d["aqi_us"]), reverse=terburuk)
    baris = [f"{i+1}. {_fmt(d)}" for i, d in enumerate(data)]
    return {"status": "ok",
            "ringkas": f"Peringkat kualitas udara Jatim ({urutan}):\n" + "\n".join(baris)}

# ═══════════════════════════════════════════════════════════════════
# ANALISA TREN / POLA HISTORIS (jangka pendek)
# Membaca field 'riwayat' dari endpoint /kota/{nama}.
# PRINSIP KEJUJURAN: hanya menyatakan pola bila cukup bukti.
#   - Pola per PERIODE waktu: disebut hanya bila selisih AQI >= AMBANG_SELISIH.
#   - Pola per HARI: disebut hanya bila selisih >= AMBANG_SELISIH DAN data >= MIN_MINGGU.
#   - SELALU dibingkai "berdasarkan pola beberapa hari terakhir", BUKAN ramalan.
# ═══════════════════════════════════════════════════════════════════
from datetime import datetime, timedelta
from collections import defaultdict

AMBANG_SELISIH = 15   # selisih AQI minimal agar suatu pola dianggap bermakna
MIN_MINGGU = 4        # minggu minimal agar klaim pola per-hari sah (cegah kesimpulan dari data tipis)

PERIODE = [("subuh", 0, 5), ("pagi", 6, 10), ("siang", 11, 14),
            ("sore", 15, 18), ("malam", 19, 23)]
HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

def _riwayat_kota(nama):
    """Ambil & parse riwayat historis satu kota. Return list (datetime, aqi, suhu, lembab)."""
    j = _ambil(f"/kota/{nama}")
    if not j or "riwayat" not in j or not j["riwayat"]:
        return None
    out = []
    for x in j["riwayat"]:
        try:
            dt = datetime.strptime(x["waktu_ambil"], "%Y-%m-%d %H:%M:%S")
            if str(x["aqi_us"]).isdigit():
                out.append((dt, int(x["aqi_us"]),
                            float(x.get("suhu_c", 0)), float(x.get("kelembaban", 0))))
        except Exception:
            continue
    return out or None

def _periode_dari_jam(jam):
    for nama, a, b in PERIODE:
        if a <= jam <= b:
            return nama
    return None

def _pola_periode(riw):
    """Rata-rata AQI per periode; tandai bermakna bila selisih >= AMBANG_SELISIH."""
    byp = defaultdict(list)
    for dt, aqi, _, _ in riw:
        p = _periode_dari_jam(dt.hour)
        if p:
            byp[p].append(aqi)
    rows = [(nama, round(sum(byp[nama]) / len(byp[nama])))
            for nama, _, _ in PERIODE if byp.get(nama)]
    if not rows:
        return None
    best = min(rows, key=lambda x: x[1])
    worst = max(rows, key=lambda x: x[1])
    return {"rows": rows, "best": best, "worst": worst,
            "selisih": worst[1] - best[1], "bermakna": (worst[1] - best[1]) >= AMBANG_SELISIH}

def _pola_hari(riw):
    """Rata-rata AQI per hari + cek kecukupan minggu (cegah klaim dari data tipis)."""
    byh = defaultdict(list)
    minggu = defaultdict(set)
    for dt, aqi, _, _ in riw:
        byh[dt.weekday()].append(aqi)
        minggu[dt.weekday()].add(dt.isocalendar()[1])
    rows = [(HARI_ID[h], round(sum(v) / len(v)), len(minggu[h])) for h, v in sorted(byh.items())]
    if len(rows) < 2:
        return None
    best = min(rows, key=lambda x: x[1])
    worst = max(rows, key=lambda x: x[1])
    min_minggu = min(r[2] for r in rows)
    selisih = worst[1] - best[1]
    # bermakna HANYA jika selisih cukup besar DAN data cukup banyak minggu
    bermakna = (selisih >= AMBANG_SELISIH) and (min_minggu >= MIN_MINGGU)
    return {"rows": rows, "best": best, "worst": worst, "selisih": selisih,
            "min_minggu": min_minggu, "bermakna": bermakna}

def _arah_tren(riw):
    """Bandingkan rata-rata 3 hari terakhir vs sebelumnya."""
    if len(riw) < 4:
        return None
    tmax = max(dt for dt, _, _, _ in riw)
    batas = tmax - timedelta(days=3)
    baru = [a for dt, a, _, _ in riw if dt >= batas]
    lama = [a for dt, a, _, _ in riw if dt < batas]
    if not baru or not lama:
        return None
    rb, rl = sum(baru) / len(baru), sum(lama) / len(lama)
    d = rb - rl
    if d > AMBANG_SELISIH * 0.5:
        arah = "cenderung sedikit naik (agak memburuk)"
    elif d < -AMBANG_SELISIH * 0.5:
        arah = "cenderung sedikit turun (agak membaik)"
    else:
        arah = "relatif stabil"
    return {"baru": round(rb), "lama": round(rl), "arah": arah}

def pola_kota(nama, periode_diminta=None, jam_diminta=None):
    """Fungsi utama tren: kembalikan RINGKASAN pola historis untuk dirangkai LLM.
    - periode_diminta: 'pagi'/'siang'/dst bila user sebut waktu umum.
    - jam_diminta: int 0-23 bila user sebut jam spesifik (cross-check).
    Semua dibingkai sebagai POLA HISTORIS, bukan ramalan.
    """
    riw = _riwayat_kota(nama)
    if not riw:
        return {"status": "error", "pesan": f"Data riwayat kota '{nama}' tidak tersedia."}

    n_hari = (max(d for d, _, _, _ in riw) - min(d for d, _, _, _ in riw)).days + 1
    pp = _pola_periode(riw)
    ph = _pola_hari(riw)
    tr = _arah_tren(riw)

    baris = [f"Pola historis {nama} berdasarkan {len(riw)} pengukuran (~{n_hari} hari terakhir). "
            f"PENTING: ini POLA MASA LALU untuk gambaran, BUKAN prediksi/ramalan kondisi tertentu."]

    # Cross-check jam spesifik bila diminta
    if jam_diminta is not None:
        byj = [a for dt, a, _, _ in riw if dt.hour == jam_diminta]
        if byj:
            rj = round(sum(byj) / len(byj))
            baris.append(f"Pada sekitar jam {jam_diminta:02d}:00, rata-rata historis AQI {rj} "
                        f"({_kategori(rj)}).")
    # Periode diminta
    if periode_diminta and pp:
        for nama_p, a in pp["rows"]:
            if nama_p == periode_diminta.lower():
                baris.append(f"Pada periode {nama_p}, rata-rata historis AQI {a} ({_kategori(a)}).")
                break

    # Pola periode umum
    if pp:
        if pp["bermakna"]:
            baris.append(f"Secara umum, udara biasanya paling bersih saat {pp['best'][0]} "
                        f"(rata-rata AQI {pp['best'][1]}) dan paling tinggi saat {pp['worst'][0]} "
                        f"(rata-rata AQI {pp['worst'][1]}).")
        else:
            baris.append("Sepanjang hari relatif stabil; belum terlihat perbedaan berarti antar waktu.")

    # Pola hari (jujur bila belum cukup data)
    if ph:
        if ph["bermakna"]:
            baris.append(f"Antar hari, {ph['best'][0]} cenderung lebih bersih dan {ph['worst'][0]} "
                        f"lebih tinggi.")
        else:
            baris.append(f"Belum ada perbedaan berarti antar hari dalam seminggu "
                        f"(data baru sekitar {ph['min_minggu']} minggu, belum cukup untuk menyimpulkan).")

    # Arah tren pendek
    if tr:
        baris.append(f"Dibanding beberapa hari sebelumnya, kondisi {tr['arah']} "
                    f"(rata-rata {tr['lama']} menjadi {tr['baru']}).")

    return {"status": "ok", "ringkas": " ".join(baris)}


if __name__ == "__main__":
    # Uji cepat fungsi saran per kategori (tanpa perlu API)
    for a in [30, 55, 94, 96, 120, 175, 250, 350]:
        print(f"AQI {a:>3} -> {_kategori(a)} | SARAN: {_saran(a)}")