"""Import seluruh data NO2 USA -> MySQL aqi_usa_no2. Adaptasi dari import ozon.
NO2: satuan ppb, rata-rata 1 jam, breakpoint EPA berbeda dari ozon."""
import pandas as pd, pymysql, time

FILE = "hourly_42602_2025.csv"
CHUNK = 500000

# Breakpoint AQI NO2 (ppb) - EPA 40 CFR App G
BP_NO2 = [(0,53,0,50),(54,100,51,100),(101,360,101,150),
          (361,649,151,200),(650,1249,201,300),(1250,1649,301,400),(1650,2049,401,500)]

def aqi_no2(ppb):
    if pd.isna(ppb) or ppb < 0: return None
    c = round(ppb)
    for c_lo,c_hi,i_lo,i_hi in BP_NO2:
        if c_lo <= c <= c_hi:
            return round((i_hi-i_lo)/(c_hi-c_lo)*(c-c_lo)+i_lo)
    return 500 if c > 2049 else None

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
cur.execute("DROP TABLE IF EXISTS aqi_usa_no2")
cur.execute("""CREATE TABLE aqi_usa_no2 (
    state VARCHAR(50), county VARCHAR(50), site INT,
    waktu DATETIME, no2_ppb FLOAT, aqi INT, kategori VARCHAR(40))""")
conn.commit()

KOLOM = ["State Name","County Name","Site Num","POC","Date GMT","Time GMT","Sample Measurement"]
total_masuk = 0
t0 = time.time()
print("Mulai import NO2...")

for i, chunk in enumerate(pd.read_csv(FILE, usecols=KOLOM, chunksize=CHUNK), 1):
    chunk = chunk.rename(columns={
        "State Name":"state","County Name":"county","Site Num":"site",
        "Sample Measurement":"no2_ppb"})
    # Filter POC terendah per stasiun (sama seperti ozon)
    poc_min = chunk.groupby(["state","county","site"])["POC"].transform("min")
    chunk = chunk[chunk["POC"]==poc_min].copy()
    # Gabung tanggal+waktu jadi datetime
    chunk["waktu"] = pd.to_datetime(chunk["Date GMT"]+" "+chunk["Time GMT"], errors="coerce")
    chunk = chunk.dropna(subset=["waktu","no2_ppb"])
    # Hitung AQI + kategori
    chunk["aqi"] = chunk["no2_ppb"].apply(aqi_no2)
    chunk = chunk.dropna(subset=["aqi"])
    chunk["aqi"] = chunk["aqi"].astype(int)
    chunk["kat"] = chunk["aqi"].apply(kategori)
    # Insert batch
    data = [(r.state, r.county, int(r.site), r.waktu.strftime("%Y-%m-%d %H:%M:%S"),
             float(r.no2_ppb), int(r.aqi), r.kat)
            for r in chunk.itertuples(index=False)]
    cur.executemany(
        "INSERT INTO aqi_usa_no2 (state,county,site,waktu,no2_ppb,aqi,kategori) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)", data)
    conn.commit()
    total_masuk += len(data)
    print(f"  chunk {i}: +{len(data):,} (total {total_masuk:,}) | {time.time()-t0:.0f}s")

# Index SETELAH insert (lebih cepat)
print("Membuat index...")
cur.execute("CREATE INDEX idx_state_waktu ON aqi_usa_no2 (state, waktu)")
cur.execute("CREATE INDEX idx_state_county_waktu ON aqi_usa_no2 (state, county, waktu)")
conn.commit()

cur.execute("SELECT COUNT(*), COUNT(DISTINCT state), COUNT(DISTINCT CONCAT(state,county,site)) FROM aqi_usa_no2")
baris, negara, stasiun = cur.fetchone()
print(f"\n✓ SELESAI dalam {time.time()-t0:.0f}s")
print(f"  {baris:,} baris, {negara} negara bagian, {stasiun} stasiun")
cur.close(); conn.close()