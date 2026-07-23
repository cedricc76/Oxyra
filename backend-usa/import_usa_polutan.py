"""Import SO2 atau CO USA -> MySQL. Pakai: python import_usa_polutan.py so2  ATAU  co"""
import pandas as pd, pymysql, time, sys

# Konfigurasi tiap polutan: file, tabel, kolom, breakpoint, satuan, pembulatan
KONFIG = {
    "so2": {
        "file":"hourly_42401_2025.csv", "tabel":"aqi_usa_so2", "kolom":"so2_ppb",
        "nama_param":"Sulfur dioxide", "bulat":True,
        "bp":[(0,35,0,50),(36,75,51,100),(76,185,101,150),(186,304,151,200),
                (305,604,201,300),(605,804,301,400),(805,1004,401,500)],
    },
    "co": {
        "file":"hourly_42101_2025.csv", "tabel":"aqi_usa_co", "kolom":"co_ppm",
        "nama_param":"Carbon monoxide", "bulat":False,
        "bp":[(0.0,4.4,0,50),(4.5,9.4,51,100),(9.5,12.4,101,150),(12.5,15.4,151,200),
                (15.5,30.4,201,300),(30.5,40.4,301,400),(40.5,50.4,401,500)],
    },
}

if len(sys.argv) < 2 or sys.argv[1] not in KONFIG:
    print("Pakai: python import_usa_polutan.py so2   ATAU   python import_usa_polutan.py co")
    sys.exit(1)

cfg = KONFIG[sys.argv[1]]
CHUNK = 500000

def hitung_aqi(nilai):
    if pd.isna(nilai) or nilai < 0: return None
    c = round(nilai) if cfg["bulat"] else round(nilai, 1)
    for c_lo,c_hi,i_lo,i_hi in cfg["bp"]:
        if c_lo <= c <= c_hi:
            return round((i_hi-i_lo)/(c_hi-c_lo)*(c-c_lo)+i_lo)
    return None

def kategori(aqi):
    if aqi is None: return None
    if aqi<=50: return "Baik"
    if aqi<=100: return "Sedang"
    if aqi<=150: return "Tidak Sehat bagi Kelompok Sensitif"
    if aqi<=200: return "Tidak Sehat"
    if aqi<=300: return "Sangat Tidak Sehat"
    return "Berbahaya"

conn = pymysql.connect(host="localhost", user="root", password="", database="oxyra_v3")
cur = conn.cursor()
cur.execute(f"DROP TABLE IF EXISTS {cfg['tabel']}")
cur.execute(f"""CREATE TABLE {cfg['tabel']} (
    state VARCHAR(50), county VARCHAR(50), site INT,
    waktu DATETIME, {cfg['kolom']} FLOAT, aqi INT, kategori VARCHAR(40))""")
conn.commit()

KOLOM = ["State Name","County Name","Site Num","POC","Date GMT","Time GMT","Sample Measurement"]
total = 0; t0 = time.time()
print(f"Import {sys.argv[1].upper()} dari {cfg['file']}...")

for i, chunk in enumerate(pd.read_csv(cfg["file"], usecols=KOLOM, chunksize=CHUNK), 1):
    chunk = chunk.rename(columns={"State Name":"state","County Name":"county",
                                    "Site Num":"site","Sample Measurement":"nilai"})
    poc_min = chunk.groupby(["state","county","site"])["POC"].transform("min")
    chunk = chunk[chunk["POC"]==poc_min].copy()
    chunk["waktu"] = pd.to_datetime(chunk["Date GMT"]+" "+chunk["Time GMT"], errors="coerce")
    chunk = chunk.dropna(subset=["waktu","nilai"])
    chunk["aqi"] = chunk["nilai"].apply(hitung_aqi)
    chunk = chunk.dropna(subset=["aqi"])
    chunk["aqi"] = chunk["aqi"].astype(int)
    chunk["kat"] = chunk["aqi"].apply(kategori)
    data = [(r.state, r.county, int(r.site), r.waktu.strftime("%Y-%m-%d %H:%M:%S"),
                float(r.nilai), int(r.aqi), r.kat) for r in chunk.itertuples(index=False)]
    cur.executemany(
        f"INSERT INTO {cfg['tabel']} (state,county,site,waktu,{cfg['kolom']},aqi,kategori) "
        f"VALUES (%s,%s,%s,%s,%s,%s,%s)", data)
    conn.commit()
    total += len(data)
    print(f"  chunk {i}: +{len(data):,} (total {total:,}) | {time.time()-t0:.0f}s")

print("Membuat index...")
cur.execute(f"CREATE INDEX idx_state_waktu ON {cfg['tabel']} (state, waktu)")
cur.execute(f"CREATE INDEX idx_state_county_waktu ON {cfg['tabel']} (state, county, waktu)")
conn.commit()
cur.execute(f"SELECT COUNT(*), COUNT(DISTINCT state), COUNT(DISTINCT CONCAT(state,county,site)) FROM {cfg['tabel']}")
b,n,s = cur.fetchone()
print(f"\n✓ {sys.argv[1].upper()} SELESAI {time.time()-t0:.0f}s | {b:,} baris, {n} negara bagian, {s} stasiun")
cur.close(); conn.close()