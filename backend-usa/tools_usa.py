"""Tools USA — 3 tingkat (negara bagian, county, titik). Multi-polutan: ozon & NO2 (Cara B)."""
import pymysql, os
DB = dict(host=os.getenv("DB_HOST", "localhost"), user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""), database="oxyra_v3", charset="utf8mb4")
def _conn(): return pymysql.connect(**DB)

# ── Peta polutan (Cara B): satu fungsi melayani banyak polutan ──
POLUTAN = {
    "ozon": {"tabel":"aqi_usa_ozone", "ring_state":"ringkasan_state",
                "ring_county":"ringkasan_county", "kolom":"ozone_ppm", "satuan":"ppm", "nama":"ozon"},
    "no2":  {"tabel":"aqi_usa_no2", "ring_state":"ringkasan_no2_state",
                "ring_county":"ringkasan_no2_county", "kolom":"no2_ppb", "satuan":"ppb", "nama":"NO2"},
    "so2":  {"tabel":"aqi_usa_so2", "ring_state":"ringkasan_so2_state",
                "ring_county":"ringkasan_so2_county", "kolom":"so2_ppb", "satuan":"ppb", "nama":"SO2"},
    "co":   {"tabel":"aqi_usa_co", "ring_state":"ringkasan_co_state",
                "ring_county":"ringkasan_co_county", "kolom":"co_ppm", "satuan":"ppm", "nama":"CO"},
}

def _pol(nama):
    """Normalisasi nama polutan dari LLM -> kunci peta. Default ozon."""
    s = str(nama or "ozon").lower().strip()
    if "no2" in s or "nitrogen" in s: return "no2"
    if "so2" in s or "sulfur" in s or "belerang" in s: return "so2"
    if s == "co" or "karbon mono" in s or "carbon mono" in s: return "co"
    return "ozon"

def _nama_lokasi(state, county, site):
    """Ambil nama lokasi stasiun dari tabel referensi. Fallback ke 'Stasiun N' kalau tidak ada."""
    conn=_conn(); cur=conn.cursor()
    cur.execute("""SELECT nama_lokasi FROM lokasi_stasiun
                    WHERE state=%s AND county=%s AND site=%s LIMIT 1""",
                (state, county, int(site)))
    r = cur.fetchone(); cur.close(); conn.close()
    return r[0] if r and r[0] else f"Stasiun {site}"

def _kategori_aqi(n):
    if n is None: return None
    n=float(n)
    if n<=50:return"Baik"
    if n<=100:return"Sedang"
    if n<=150:return"Tidak Sehat bagi Kelompok Sensitif"
    if n<=200:return"Tidak Sehat"
    if n<=300:return"Sangat Tidak Sehat"
    return"Berbahaya"

def bandingkan_negara_bagian(urutan: str = "terburuk", limit: int = 10, polutan: str = "ozon"):
    """Perbandingan rata-rata AQI antar negara bagian (dari tabel ringkasan). Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    arah = "DESC" if urutan=="terburuk" else "ASC"
    cur.execute(f"""SELECT state, aqi_rata, aqi_maks, jumlah_stasiun
                    FROM {cfg['ring_state']} ORDER BY aqi_rata {arah} LIMIT %s""", (limit,))
    rows=cur.fetchall(); cur.close(); conn.close()
    return {"status":"ok","tingkat":"negara_bagian","urutan":urutan,"polutan":cfg["nama"],
            "data":[{"negara_bagian":r["state"],"aqi_rata":float(r["aqi_rata"]),
                        "aqi_maks":r["aqi_maks"],"jumlah_stasiun":r["jumlah_stasiun"]} for r in rows]}

def bandingkan_county(state: str, urutan: str = "terburuk", limit: int = 10, polutan: str = "ozon"):
    """Perbandingan rata-rata AQI antar county dalam satu negara bagian. Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    arah = "DESC" if urutan=="terburuk" else "ASC"
    cur.execute(f"""SELECT county, aqi_rata, aqi_maks, jumlah_stasiun
                    FROM {cfg['ring_county']} WHERE state=%s
                    ORDER BY aqi_rata {arah} LIMIT %s""", (state, limit))
    rows=cur.fetchall(); cur.close(); conn.close()
    if not rows: return {"status":"tidak_ada_data","state":state}
    return {"status":"ok","tingkat":"county","negara_bagian":state,"urutan":urutan,"polutan":cfg["nama"],
            "data":[{"county":r["county"],"aqi_rata":float(r["aqi_rata"]),
                        "aqi_maks":r["aqi_maks"],"jumlah_stasiun":r["jumlah_stasiun"]} for r in rows]}

def kondisi_titik(state: str, county: str, waktu: str = None, polutan: str = "ozon"):
    """Data spesifik (per jam, bukan rata-rata) di satu county. Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    kolom, tabel = cfg["kolom"], cfg["tabel"]
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    if waktu:
        cur.execute(f"""SELECT site, waktu, {kolom} AS nilai, aqi, kategori FROM {tabel}
                        WHERE state=%s AND county=%s AND DATE(waktu)=%s
                        ORDER BY waktu DESC LIMIT 10""", (state, county, waktu))
    else:
        cur.execute(f"""SELECT site, waktu, {kolom} AS nilai, aqi, kategori FROM {tabel}
                        WHERE state=%s AND county=%s
                        ORDER BY waktu DESC LIMIT 10""", (state, county))
    rows=cur.fetchall(); cur.close(); conn.close()
    if not rows: return {"status":"tidak_ada_data","state":state,"county":county,"polutan":cfg["nama"]}
    return {"status":"ok","tingkat":"titik","negara_bagian":state,"county":county,
            "polutan":cfg["nama"],"satuan":cfg["satuan"],
            "data":[{"site":r["site"],
                        "nama_lokasi":_nama_lokasi(state, county, r["site"]),
                        "waktu":r["waktu"].strftime("%Y-%m-%d %H:%M"),
                        "nilai":r["nilai"],"aqi":r["aqi"],"kategori":r["kategori"]} for r in rows]}

def cari_lokasi_terbaik(state: str, county: str = None, jam: int = None, limit: int = 5, polutan: str = "ozon"):
    """Cari lokasi udara TERBAIK untuk rekomendasi aktivitas (penalaran cerdas, bukan rata-rata buta).
    - county diberikan -> bandingkan antar-STASIUN dalam county.
    - hanya state -> bandingkan antar-COUNTY dalam state.
    - jam diberikan (0-23) -> pakai POLA pada jam itu; tanpa jam -> rata-rata keseluruhan.
    Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    tabel = cfg["tabel"]
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    filter_jam = "AND HOUR(waktu)=%s" if jam is not None else ""

    if county:  # level stasiun dalam county
        params = [state, county] + ([jam] if jam is not None else [])
        cur.execute(f"""SELECT site, ROUND(AVG(aqi),1) aqi_rata, COUNT(*) n
                        FROM {tabel}
                        WHERE state=%s AND county=%s {filter_jam}
                        GROUP BY site ORDER BY aqi_rata ASC""", params)
        rows=cur.fetchall(); cur.close(); conn.close()
        if not rows: return {"status":"tidak_ada_data","state":state,"county":county}
        unit, label = "site", "stasiun"
    else:  # level county dalam state
        params = [state] + ([jam] if jam is not None else [])
        cur.execute(f"""SELECT county AS site, ROUND(AVG(aqi),1) aqi_rata, COUNT(*) n
                        FROM {tabel} WHERE state=%s {filter_jam}
                        GROUP BY county ORDER BY aqi_rata ASC""", params)
        rows=cur.fetchall(); cur.close(); conn.close()
        if not rows: return {"status":"tidak_ada_data","state":state}
        unit, label = "county", "county"

    rata_umum = round(sum(float(r["aqi_rata"]) for r in rows)/len(rows), 1)
    tidak_sehat = [r for r in rows if float(r["aqi_rata"]) > 100]
    terbaik = rows[0]
    return {
        "status":"ok", "level":label, "state":state, "county":county,
        "jam": jam, "polutan": cfg["nama"],
        "kondisi_umum_aqi": rata_umum,
        "kondisi_umum_kategori": _kategori_aqi(rata_umum),
        "jumlah_titik": len(rows),
        "jumlah_tidak_sehat": len(tidak_sehat),
        "mayoritas_tidak_sehat": len(tidak_sehat) > len(rows)/2,
        "terbaik": {unit: (_nama_lokasi(state, county, terbaik["site"]) if label=="stasiun" else terbaik["site"]),
                    "aqi_rata": float(terbaik["aqi_rata"]),
                    "kategori": _kategori_aqi(float(terbaik["aqi_rata"]))},
        "semua": [{unit: (_nama_lokasi(state, county, r["site"]) if label=="stasiun" else r["site"]),
                    "aqi_rata": float(r["aqi_rata"]),
                    "kategori": _kategori_aqi(float(r["aqi_rata"]))} for r in rows[:limit]],
    }

def _filter_level(state, county, site):
    """Bangun klausa WHERE + params sesuai level yang diberikan."""
    klausa, params = ["state=%s"], [state]
    if county:
        klausa.append("county=%s"); params.append(county)
    if site is not None:
        klausa.append("site=%s"); params.append(site)
    return " AND ".join(klausa), params

def pola_harian(state: str, county: str = None, site: int = None, polutan: str = "ozon"):
    """Pola per JAM (jam berapa puncak/terendah) di level mana pun. Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    where, params = _filter_level(state, county, site)
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(f"""SELECT HOUR(waktu) jam, ROUND(AVG(aqi),1) rata, COUNT(*) n
                    FROM {cfg['tabel']} WHERE {where}
                    GROUP BY HOUR(waktu) ORDER BY jam""", params)
    rows=cur.fetchall(); cur.close(); conn.close()
    if not rows: return {"status":"tidak_ada_data","state":state,"county":county,"site":site}
    data=[(r["jam"], float(r["rata"])) for r in rows]
    jp, ap = max(data, key=lambda x:x[1])
    jr, ar = min(data, key=lambda x:x[1])
    level = "stasiun" if site is not None else ("county" if county else "negara_bagian")
    return {"status":"ok","level":level,"state":state,"county":county,"site":site,"polutan":cfg["nama"],
            "jam_puncak":jp,"aqi_puncak":round(ap,1),
            "jam_terendah":jr,"aqi_terendah":round(ar,1),
            "pola":[{"jam":j,"aqi":round(a,1)} for j,a in data]}

def tren_periode(state: str, tanggal_mulai: str, tanggal_akhir: str,
                    county: str = None, site: int = None, polutan: str = "ozon"):
    """Tren (membaik/memburuk/stabil) sepanjang periode di level mana pun. Mendukung ozon & NO2."""
    cfg = POLUTAN[_pol(polutan)]
    where, params = _filter_level(state, county, site)
    conn=_conn(); cur=conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(f"""SELECT COUNT(*) n, ROUND(AVG(aqi),1) rata, MIN(aqi) mn, MAX(aqi) mx
                    FROM {cfg['tabel']} WHERE {where} AND DATE(waktu) BETWEEN %s AND %s""",
                params+[tanggal_mulai, tanggal_akhir])
    s=cur.fetchone()
    if not s or not s["n"]:
        cur.close(); conn.close()
        return {"status":"tidak_ada_data","state":state,"county":county,"site":site}
    cur.execute(f"""SELECT DATE(waktu) tgl, AVG(aqi) rata
                    FROM {cfg['tabel']} WHERE {where} AND DATE(waktu) BETWEEN %s AND %s
                    GROUP BY DATE(waktu) ORDER BY tgl""",
                params+[tanggal_mulai, tanggal_akhir])
    harian=[float(r["rata"]) for r in cur.fetchall()]
    cur.close(); conn.close()
    arah="stabil"
    if len(harian)>=2:
        t=len(harian)//2
        awal=sum(harian[:t])/max(t,1); akhir=sum(harian[t:])/max(len(harian)-t,1)
        beda=akhir-awal
        if beda>3: arah="memburuk"
        elif beda<-3: arah="membaik"
    level = "stasiun" if site is not None else ("county" if county else "negara_bagian")
    return {"status":"ok","level":level,"state":state,"county":county,"site":site,"polutan":cfg["nama"],
            "periode":f"{tanggal_mulai} s/d {tanggal_akhir}",
            "rata_rata_aqi":float(s["rata"]),"aqi_min":s["mn"],"aqi_max":s["mx"],
            "arah_tren":arah}

if __name__ == "__main__":
    import json
    print("=== NO2 negara bagian (terburuk) ===")
    print(json.dumps(bandingkan_negara_bagian("terburuk", 5, polutan="no2"), indent=2, default=str))
    print("\n=== Ozon negara bagian (default, harus sama spt dulu) ===")
    print(json.dumps(bandingkan_negara_bagian("terburuk", 5), indent=2, default=str))
    print("\n=== NO2 kondisi titik LA ===")
    print(json.dumps(kondisi_titik("California", "Los Angeles", polutan="no2"), indent=2, default=str))