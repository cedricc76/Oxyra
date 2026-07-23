"""Ambil daftar negara bagian & county valid dari DB, simpan ke file untuk validasi."""
import pymysql, json
conn = pymysql.connect(host="localhost", user="root", password="", database="oxyra_v3")
cur = conn.cursor()

cur.execute("SELECT DISTINCT state FROM ringkasan_state ORDER BY state")
states = [r[0] for r in cur.fetchall()]

cur.execute("SELECT DISTINCT state, county FROM ringkasan_county ORDER BY state, county")
counties = {}
for st, co in cur.fetchall():
    counties.setdefault(st, []).append(co)

cur.close(); conn.close()

data = {"states": states, "counties": counties}
with open("wilayah_valid.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✓ {len(states)} negara bagian, {sum(len(c) for c in counties.values())} county")
print(f"Contoh negara bagian: {states[:5]}")
print(f"County California: {counties.get('California', [])[:5]}")