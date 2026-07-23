"""Import SEMUA data ozone EPA (seluruh AS, 5.8 juta baris) -> MySQL aqi_usa_ozone.
Efisien: baca per potongan, insert per batch, index dibuat di akhir."""
import pandas as pd, pymysql, time

CSV = "hourly_44201_2025.csv"
DB = dict(host="localhost", user="root", password="", database="oxyra_v3", charset="utf8mb4")
CHUNK = 500000   # baca 500rb baris per potongan

# Rumus AQI ozone 8-jam (EPA) — ppm, terverifikasi
BP_O3 = [(0.000,0.054,0,50),(0.055,0.070,51,100),(0.071,0.085,101,150),
         (0.086,0.105,151,200),(0.106,0.200,201,300),(0.201,0.604,301,500)]
def aqi_ozone(c):
    if pd.isna(c) or c < 0: return None
    c = round(float(c), 3)
    for clo,chi,ilo,ihi in BP_O3:
        if clo <= c <= chi: return round((ihi-ilo)/(chi-clo)*(c-clo)+ilo)
    return 500 if c > 0.604 else None
def kategori(a):
    if a is None: return None
    if a<=50:return"Baik"
    if a<=100:return"Sedang"
    if a<=150:return"Tidak Sehat bagi Kelompok Sensitif"
    if a<=200:return"Tidak Sehat"
    if a<=300:return"Sangat Tidak Sehat"
    return"Berbahaya"

# ── Siapkan tabel (tanpa index dulu, supaya insert cepat) ──
conn = pymysql.connect(**DB); cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS aqi_usa_ozone")
cur.execute("""
    CREATE TABLE aqi_usa_ozone (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(40), county VARCHAR(60), site INT,
        waktu DATETIME, ozone_ppm FLOAT, aqi INT, kategori VARCHAR(40)
    ) CHARACTER SET utf8mb4
""")
conn.commit()

# ── Baca per potongan, olah, insert per batch ──
SQL = """INSERT INTO aqi_usa_ozone (state,county,site,waktu,ozone_ppm,aqi,kategori)
         VALUES (%s,%s,%s,%s,%s,%s,%s)"""
total = 0
t0 = time.time()
kolom = ["State Name","County Name","Site Num","POC","Date Local","Time Local","Sample Measurement"]

for i, chunk in enumerate(pd.read_csv(CSV, usecols=kolom, chunksize=CHUNK, low_memory=False)):
    # POC terendah per stasiun (state+county+site)
    chunk["_stasiun"] = chunk["State Name"]+"|"+chunk["County Name"]+"|"+chunk["Site Num"].astype(str)
    poc_min = chunk.groupby("_stasiun")["POC"].transform("min")
    chunk = chunk[chunk["POC"] == poc_min]

    chunk["waktu"] = pd.to_datetime(chunk["Date Local"]+" "+chunk["Time Local"], errors="coerce")
    chunk = chunk.dropna(subset=["waktu"])
    chunk["ppm"] = pd.to_numeric(chunk["Sample Measurement"], errors="coerce")
    chunk["aqi"] = chunk["ppm"].apply(aqi_ozone)
    chunk = chunk.dropna(subset=["aqi"])
    chunk["kat"] = chunk["aqi"].apply(kategori)

    sub = chunk[["State Name","County Name","Site Num","waktu","ppm","aqi","kat"]].rename(
            columns={"State Name":"state","County Name":"county","Site Num":"site"})
    data = [
            (r.state, r.county, int(r.site), r.waktu.strftime("%Y-%m-%d %H:%M:%S"),
            None if pd.isna(r.ppm) else float(r.ppm), int(r.aqi), r.kat)
            for r in sub.itertuples(index=False)
        ]
    if data:
        cur.executemany(SQL, data)
        conn.commit()
        total += len(data)
    print(f"  potongan {i+1}: total tersimpan {total:,} ({time.time()-t0:.0f}s)")

print(f"\n✓ Selesai insert {total:,} baris ({time.time()-t0:.0f} detik)")

# ── Buat index SETELAH insert (jauh lebih cepat) ──
print("Membuat index...")
cur.execute("CREATE INDEX idx_state_waktu ON aqi_usa_ozone (state, waktu)")
cur.execute("CREATE INDEX idx_state_county_waktu ON aqi_usa_ozone (state, county, waktu)")
conn.commit()
print("✓ Index selesai")

# ── Ringkasan ──
cur.execute("SELECT COUNT(*), COUNT(DISTINCT state), COUNT(DISTINCT CONCAT(state,county,site)) FROM aqi_usa_ozone")
n, ns, nstasiun = cur.fetchone()
print(f"\nRingkasan: {n:,} baris | {ns} negara bagian | {nstasiun:,} stasiun")
cur.close(); conn.close()