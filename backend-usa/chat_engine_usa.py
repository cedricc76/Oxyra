"""
Mesin chat Oxyra v3 — versi USA (4 polutan: O3, NO2, SO2, CO; hierarki 3 tingkat).
LLM: pilih tool + tulis jawaban. KODE: jamin akurasi + validasi wilayah (anti-halusinasi).
Tingkat: negara bagian (rata-rata) -> county (rata-rata) -> titik (data asli per jam).
"""
import httpx, json, re
import os
from tools_usa import (bandingkan_negara_bagian, bandingkan_county, kondisi_titik,
                    cari_lokasi_terbaik, pola_harian, tren_periode)
from rag import cari as rag_cari

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPSI_LLM = {"temperature": 0.2, "seed": 42}
DEBUG = True   # set False untuk matikan cetak diagnosa argumen LLM

# ── Muat daftar wilayah valid (untuk validasi ketat anti-halusinasi) ──
with open("wilayah_valid.json", encoding="utf-8") as f:
    WILAYAH = json.load(f)
STATES_LOWER = {s.lower(): s for s in WILAYAH["states"]}
COUNTIES_LOWER = {st.lower(): {c.lower(): c for c in cs}
                    for st, cs in WILAYAH["counties"].items()}

def _state_valid(nama):
    """Kembalikan nama kanonik kalau valid, None kalau tidak (mis. halusinasi 'Jakarta')."""
    if not nama: return None
    return STATES_LOWER.get(str(nama).lower().strip())

def _county_valid(state_kanonik, nama_county):
    if not state_kanonik or not nama_county: return None
    nm = str(nama_county).lower().strip()
    # LLM sering menambah "county" di belakang (mis. "San Bernardino County") — buang
    if nm.endswith(" county"):
        nm = nm[:-len(" county")].strip()
    return COUNTIES_LOWER.get(state_kanonik.lower(), {}).get(nm)

def _normalisasi_urutan(nilai):
    """Apa pun yang LLM kirim -> 'terburuk' atau 'terbaik' (default terburuk)."""
    s = str(nilai).lower().strip()
    if s in ("terbaik", "terbersih", "bersih", "terendah", "rendah", "best", "cleanest"):
        return "terbaik"
    return "terburuk"   # default: terburuk (termasuk 'tertinggi', 'buruk', kosong, dll)

def _normalisasi_limit(nilai, default=10):
    try:
        n = int(nilai)
        return n if 1 <= n <= 53 else default
    except (ValueError, TypeError):
        return default

# ── Tool schema untuk Ollama ──
TOOLS_SCHEMA = [
    {"type":"function","function":{
        "name":"bandingkan_negara_bagian",
        "description":"Bandingkan rata-rata kualitas udara (ozon, NO2, SO2, atau CO) antar negara bagian AS. Untuk 'negara bagian mana yang ozonnya/NO2-nya/SO2-nya/CO-nya terburuk/terbaik'",
        "parameters":{"type":"object","properties":{
            "urutan":{"type":"string","enum":["terburuk","terbaik"],"description":"terburuk=AQI tertinggi, terbaik=terendah"},
            "limit":{"type":"integer","description":"berapa banyak (default 10)"},
            "polutan":{"type":"string","enum":["ozon","no2","so2","co"],"description":"polutan sesuai yang disebut pengguna: ozon (default), no2, so2, atau co"}
        }}}},
    {"type":"function","function":{
        "name":"bandingkan_county",
        "description":"Bandingkan rata-rata kualitas udara (ozon, NO2, SO2, atau CO) antar county/kota DI DALAM satu negara bagian. Untuk 'kota mana di California yang terburuk'",
        "parameters":{"type":"object","properties":{
            "state":{"type":"string","description":"nama negara bagian, mis. California"},
            "urutan":{"type":"string","enum":["terburuk","terbaik"]},
            "limit":{"type":"integer"},
            "polutan":{"type":"string","enum":["ozon","no2","so2","co"],"description":"polutan sesuai yang disebut pengguna: ozon (default), no2, so2, atau co"}
        },"required":["state"]}}},
    {"type":"function","function":{
        "name":"kondisi_titik",
        "description":"Data kualitas udara (ozon, NO2, SO2, atau CO) spesifik per jam (bukan rata-rata) di satu county. Untuk 'kondisi udara/NO2/SO2/CO di Los Angeles'",
        "parameters":{"type":"object","properties":{
            "state":{"type":"string"},
            "county":{"type":"string"},
            "waktu":{"type":"string","description":"YYYY-MM-DD (opsional)"},
            "polutan":{"type":"string","enum":["ozon","no2","so2","co"],"description":"polutan sesuai yang disebut pengguna: ozon (default), no2, so2, atau co"}
        },"required":["state","county"]}}},
    {"type":"function","function":{
        "name":"cari_lokasi_terbaik",
        "description":"Cari lokasi udara TERBAIK untuk rekomendasi aktivitas/olahraga. Untuk 'di mana sebaiknya olahraga', 'tempat paling sehat untuk aktivitas di luar'. Bisa per stasiun (jika county disebut) atau per county (jika hanya negara bagian).",
        "parameters":{"type":"object","properties":{
            "state":{"type":"string","description":"nama negara bagian"},
            "county":{"type":"string","description":"nama county (opsional, untuk cari antar-stasiun)"},
            "jam":{"type":"integer","description":"jam 0-23 jika pengguna sebut waktu (mis. 'jam 9 pagi'=9)"}
        },"required":["state"]}}},
    {"type":"function","function":{
        "name":"pola_harian",
        "description":"Pola ozon dalam sehari (jam berapa biasanya tertinggi/terendah). Untuk 'jam berapa ozon paling tinggi di California', 'kapan waktu terbaik dalam sehari'. Bisa level negara bagian, county, atau stasiun.",
        "parameters":{"type":"object","properties":{
            "state":{"type":"string"},
            "county":{"type":"string","description":"opsional"},
            "site":{"type":"integer","description":"opsional, nomor stasiun"}
        },"required":["state"]}}},
    {"type":"function","function":{
        "name":"tren_periode",
        "description":"Tren ozon (membaik/memburuk/stabil) sepanjang rentang tanggal. Untuk 'apakah udara California membaik Januari 2025'. Butuh tanggal mulai & akhir.",
        "parameters":{"type":"object","properties":{
            "state":{"type":"string"},
            "tanggal_mulai":{"type":"string","description":"YYYY-MM-DD"},
            "tanggal_akhir":{"type":"string","description":"YYYY-MM-DD"},
            "county":{"type":"string","description":"opsional"},
            "site":{"type":"integer","description":"opsional"}
        },"required":["state","tanggal_mulai","tanggal_akhir"]}}},
]
TOOL_FUNCTIONS = {
    "bandingkan_negara_bagian": bandingkan_negara_bagian,
    "bandingkan_county": bandingkan_county,
    "kondisi_titik": kondisi_titik,
    "cari_lokasi_terbaik": cari_lokasi_terbaik,
    "pola_harian": pola_harian,
    "tren_periode": tren_periode,
}

SYSTEM_PROMPT = """Kamu Oxyra, asisten kualitas udara (data 4 polutan: O3, NO2, SO2, CO, seluruh Amerika Serikat).
- Untuk pertanyaan perbandingan wilayah, kondisi suatu negara bagian/kota/titik, atau data polutan -> pilih tool yang tepat.
- Pertanyaan edukatif ('apa itu ozon', 'kenapa polusi berbahaya') -> jawab dari pengetahuan umum, bahasa sederhana, tanpa angka/lokasi, jangan buka dengan 'maaf'.
- Nama negara bagian & county dalam bahasa Inggris sesuai data resmi (mis. California, Los Angeles).
- Bahasa Indonesia sederhana dan ramah. Jangan sebut kata 'tool' atau proses internalmu."""

EDU_KEYWORDS = ["apa itu","apa yang dimaksud","kenapa","mengapa","jelaskan","fungsi","dampak","bahaya"]
DATA_KEYWORDS = ["tren","kondisi","kualitas udara","ozon","level","tertinggi","terendah",
                    "terburuk","terbaik","bandingkan","perbandingan","negara bagian","county","kota","wilayah"]

def _jawab_tanpa_tool(pertanyaan, model):
    q = pertanyaan.lower()
    edukatif = any(k in q for k in EDU_KEYWORDS)
    minta_data = any(k in q for k in DATA_KEYWORDS)
    # Pertanyaan yang jelas minta DATA wilayah tapi tak sebut wilayah valid -> arahkan jujur
    if minta_data and not edukatif:
        return ("Saya memiliki data kualitas udara (4 polutan: O3, NO2, SO2, CO) dari stasiun pemantau di seluruh Amerika Serikat "
                "(53 negara bagian). Silakan sebutkan wilayahnya — misalnya \"negara bagian mana "
                "yang ozonnya terburuk?\", \"kota mana di California yang terburuk?\", atau "
                "\"kondisi udara di Los Angeles\".")

    # RAG: cari entri pengetahuan relevan (bisa kosong kalau di luar topik)
    try:
        entri = rag_cari(pertanyaan, top_k=2)
    except Exception:
        entri = []   # kalau RAG gagal, lanjut tanpa acuan (chatbot tetap jalan)

    sys_edu_rag = (
        "Kamu Oxyra, asisten kualitas udara yang ramah. "
        "Jawab pertanyaan pengguna dengan natural dan mengalir. "
        "Jika informasi REFERENSI di bawah relevan dengan pertanyaan, gunakan sebagai dasar "
        "jawaban agar akurat. Jika tidak relevan, abaikan saja dan jawab dari pengetahuan umummu. "
        "JANGAN PERNAH menyebut kata 'acuan', 'referensi', atau menjelaskan proses berpikirmu. "
        "Langsung jawab pertanyaannya seolah kamu memang tahu. "
        "JANGAN mengarang data/angka/kondisi wilayah; kamu punya data 4 polutan (O3, NO2, SO2, CO) stasiun AS. "
        "Bahasa Indonesia sederhana dan ramah."
    )
    if entri:
        referensi = "\n".join(f"- {e['topik']}: {e['isi']}" for e in entri)
        konten = f"Pertanyaan: {pertanyaan}\n\nREFERENSI:\n{referensi}"
    else:
        konten = pertanyaan   # tanpa acuan -> LLM jawab normal (luwes)

    r = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "stream": False, "options": OPSI_LLM,
        "messages": [{"role":"system","content":sys_edu_rag},
                        {"role":"user","content":konten}],
    }, timeout=120)
    return _bersihkan(r.json()["message"].get("content",""))

def _kategori(n):
    if n is None: return None
    n=float(n)
    if n<=50:return"Baik"
    if n<=100:return"Sedang"
    if n<=150:return"Tidak Sehat bagi Kelompok Sensitif"
    if n<=200:return"Tidak Sehat"
    if n<=300:return"Sangat Tidak Sehat"
    return"Berbahaya"

def _fakta_dan_instruksi(nama_tool, hasil):
    if hasil.get("status") != "ok":
        return ("Data tidak tersedia.", "Sampaikan jujur & singkat bahwa datanya belum tersedia.")

    if nama_tool == "bandingkan_negara_bagian":
        baris = [f"{i+1}. {d['negara_bagian']}: rata-rata AQI {d['aqi_rata']} "
                    f"({_kategori(d['aqi_rata'])}), {d['jumlah_stasiun']} stasiun"
                    for i, d in enumerate(hasil["data"])]
        pol = hasil.get("polutan", "ozon")
        fakta = f"Peringkat negara bagian ({hasil['urutan']}) berdasarkan rata-rata AQI {pol}:\n" + "\n".join(baris)
        instruksi = ("Sampaikan sebagai peringkat/perbandingan yang jelas dan mengalir. "
                        "TEKANKAN ini RATA-RATA seluruh stasiun & waktu di tiap negara bagian "
                        "(gambaran umum, bukan kondisi satu titik). Sebut beberapa teratas dengan angkanya. "
                        "JANGAN mengarang negara bagian atau angka di luar yang diberikan.")
        return fakta, instruksi

    if nama_tool == "bandingkan_county":
        baris = [f"{i+1}. {d['county']}: rata-rata AQI {d['aqi_rata']} "
                    f"({_kategori(d['aqi_rata'])}), {d['jumlah_stasiun']} stasiun"
                    for i, d in enumerate(hasil["data"])]
        pol = hasil.get("polutan", "ozon")
        fakta = (f"Peringkat county di {hasil['negara_bagian']} ({hasil['urutan']}) "
                    f"berdasarkan rata-rata AQI {pol}:\n" + "\n".join(baris))
        instruksi = ("Sampaikan sebagai perbandingan county DALAM negara bagian tersebut, mengalir. "
                        "TEKANKAN ini rata-rata. Sebut beberapa teratas dengan angkanya. "
                        "JANGAN mengarang county atau angka.")
        return fakta, instruksi

    if nama_tool == "kondisi_titik":
        d = hasil["data"]
        pol = hasil.get("polutan", "ozon")
        sat = hasil.get("satuan", "")
        ringkas = [f"{x.get('nama_lokasi', 'Stasiun '+str(x['site']))}: AQI {x['aqi']} ({x['kategori']}), {pol} {x['nilai']} {sat}"
                    for x in d[:8]]
        waktu = d[0]["waktu"] if d else "-"
        fakta = (f"Data {pol} spesifik di {hasil['county']}, {hasil['negara_bagian']} "
                    f"(data terakhir tersedia {waktu}):\n" + "\n".join(ringkas))
        instruksi = ("Sampaikan kondisi titik-titik ini dalam bahasa awam, 2-4 kalimat. "
                        "Ini DATA ASLI per stasiun (bukan rata-rata). Sebut kondisi umumnya (mis. mayoritas Baik) "
                        "dan boleh sebut variasi antar stasiun. Sebut waktu sebagai 'data terakhir tersedia', "
                        "JANGAN pakai 'saat ini'. JANGAN mengarang stasiun/angka lain.")
        return fakta, instruksi

    if nama_tool == "cari_lokasi_terbaik":
        unit = "" if hasil["level"]=="stasiun" else "County"
        kunci = "site" if hasil["level"]=="stasiun" else "county"
        t = hasil["terbaik"]
        konteks_jam = f" pada jam {hasil['jam']:02d}:00" if hasil.get("jam") is not None else ""
        daftar = ", ".join(f"{unit} {x[kunci]} (AQI {x['aqi_rata']})" for x in hasil["semua"][:3])
        fakta = (f"Wilayah: {hasil['state']}{(', '+hasil['county']) if hasil.get('county') else ''}{konteks_jam}. "
                    f"Kondisi umum: rata-rata AQI {hasil['kondisi_umum_aqi']} ({hasil['kondisi_umum_kategori']}). "
                    f"Dari {hasil['jumlah_titik']} titik, {hasil['jumlah_tidak_sehat']} tergolong tidak sehat. "
                    f"Lokasi TERBAIK: {unit} {t[kunci]} (rata-rata AQI {t['aqi_rata']}, {t['kategori']}). "
                    f"Beberapa terbaik: {daftar}.")
        if hasil["mayoritas_tidak_sehat"]:
            instruksi = ("Untuk ORANG AWAM. Mulai dari INTI: secara umum wilayah ini KURANG sehat untuk "
                            "aktivitas luar. TAPI beri solusi: kalau tetap ingin olahraga, sebutkan lokasi TERBAIK "
                            "sebagai rekomendasi. Tulis ringkas & praktis. Angka AQI HANYA sebagai pelengkap singkat "
                            "di akhir (dalam tanda kurung), jangan jadi fokus. Berdasarkan data historis. 2-3 kalimat.")
        else:
            instruksi = ("Untuk ORANG AWAM. Mulai dari INTI: secara umum wilayah ini relatif aman untuk aktivitas "
                            "luar, dan sebutkan lokasi TERBAIK sebagai rekomendasi utama. Ringkas & praktis. "
                            "Angka AQI HANYA pelengkap singkat di akhir (dalam kurung), jangan jadi fokus. "
                            "Berdasarkan data historis. 2-3 kalimat.")
        return fakta, instruksi

    if nama_tool == "pola_harian":
        lv = {"negara_bagian":hasil["state"],
            "county":f"{hasil.get('county')}, {hasil['state']}" if hasil.get('county') else hasil["state"],
            "stasiun":f"Stasiun {hasil.get('site')} ({hasil['state']})"}[hasil["level"]]
        fakta = (f"Pola harian ozon di {lv}. "
                f"Tertinggi pada jam {hasil['jam_puncak']:02d}:00 (rata-rata AQI {hasil['aqi_puncak']}). "
                f"Terendah pada jam {hasil['jam_terendah']:02d}:00 (rata-rata AQI {hasil['aqi_terendah']}).")
        instruksi = ("Jelaskan pola harian ozon 2-3 kalimat awam. Sebut jam tertinggi & terendah. "
                    "Boleh tambah penjelasan singkat: ozon permukaan naik siang hari karena sinar matahari, "
                    "turun malam/pagi. Berdasarkan DATA HISTORIS. JANGAN mengarang angka lain.")
        return fakta, instruksi

    if nama_tool == "tren_periode":
        lv = (f"{hasil.get('county')}, {hasil['state']}" if hasil.get('county') else hasil["state"])
        fakta = (f"Tren ozon di {lv}. Periode: {hasil['periode']}. "
                f"Rata-rata AQI: {hasil['rata_rata_aqi']} ({_kategori(hasil['rata_rata_aqi'])}). "
                f"Terendah {hasil['aqi_min']}, tertinggi {hasil['aqi_max']}. Arah: {hasil['arah_tren']}.")
        instruksi = ("Sampaikan TREN 2-4 kalimat awam. Tekankan ini rata-rata sepanjang periode. "
                    "Sebut arahnya (membaik/memburuk/stabil) dan rentang terendah-tertinggi. "
                    "Kalau ada selisih besar min-max, boleh sebut ada lonjakan sesekali. "
                    "Berdasarkan DATA HISTORIS. JANGAN mengarang.")
        return fakta, instruksi

    return (json.dumps(hasil, ensure_ascii=False, default=str), "Sampaikan data ini dengan jelas.")

def _bersihkan(teks):
    if not teks: return ""
    teks = re.sub(r'\{[^{}]*["\']name["\']\s*:[^{}]*["\'](?:parameters|arguments)["\'][^{}]*\}',
                    '', teks, flags=re.DOTALL).strip()
    return "" if len(teks) <= 2 else teks

def chat(pertanyaan: str, model: str = "llama3.1:8b") -> dict:
    # Langkah 1: LLM pilih tool
    r = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "tools": TOOLS_SCHEMA, "stream": False, "options": OPSI_LLM,
        "messages": [{"role":"system","content":SYSTEM_PROMPT},
                        {"role":"user","content":pertanyaan}],
    }, timeout=120)
    tool_calls = r.json()["message"].get("tool_calls", [])
    if not tool_calls:
        return {"reply": _jawab_tanpa_tool(pertanyaan, model), "tools_dipakai": [], "model": model, "data": ""}

    # Saring + validasi wilayah (anti-halusinasi) + normalisasi argumen
    valid_calls = []
    for tc in tool_calls:
        nama = tc["function"]["name"]
        args = dict(tc["function"]["arguments"])
        if DEBUG:
            print(f"  [debug] {nama} args dari LLM: {args}")

        if nama == "bandingkan_negara_bagian":
            args["urutan"] = _normalisasi_urutan(args.get("urutan"))
            args["limit"] = _normalisasi_limit(args.get("limit"))
            valid_calls.append((nama, args))

        elif nama == "bandingkan_county":
            st = _state_valid(args.get("state"))
            if st:
                args["state"] = st
                args["urutan"] = _normalisasi_urutan(args.get("urutan"))
                args["limit"] = _normalisasi_limit(args.get("limit"))
                valid_calls.append((nama, args))

        elif nama == "kondisi_titik":
            st = _state_valid(args.get("state"))
            co = _county_valid(st, args.get("county")) if st else None
            if st and co:
                args["state"], args["county"] = st, co
                valid_calls.append((nama, args))

        elif nama == "cari_lokasi_terbaik":
            st = _state_valid(args.get("state"))
            if st:
                args["state"] = st
                co = _county_valid(st, args.get("county")) if args.get("county") else None
                if co: args["county"] = co
                elif "county" in args: args.pop("county")  # county ngawur dibuang, tetap jalan di level state
                # normalisasi jam
                try:
                    j = int(args.get("jam"))
                    args["jam"] = j if 0 <= j <= 23 else None
                except (ValueError, TypeError):
                    args.pop("jam", None)
                valid_calls.append((nama, args))

        elif nama in ("pola_harian", "tren_periode"):
            st = _state_valid(args.get("state"))
            if st:
                args["state"] = st
                co = _county_valid(st, args.get("county")) if args.get("county") else None
                if co: args["county"] = co
                elif "county" in args: args.pop("county")
                # site biarkan apa adanya (divalidasi saat query; kalau ngawur -> tidak_ada_data)
                valid_calls.append((nama, args))

    if not valid_calls:
        return {"reply": _jawab_tanpa_tool(pertanyaan, model), "tools_dipakai": [], "model": model, "data": ""}

    # Langkah 2: eksekusi tool + rakit fakta (oleh KODE)
    tools_dipakai, fakta_semua, instruksi_semua = [], [], []
    for nama, args in valid_calls:
        tools_dipakai.append(nama)
        fungsi = TOOL_FUNCTIONS[nama]
        if "waktu" in args:
            t = str(args["waktu"]).lower().strip()
            if t in ("hari ini","sekarang","null","none","") or not t[:4].isdigit():
                args.pop("waktu", None)
        valid = fungsi.__code__.co_varnames[:fungsi.__code__.co_argcount]
        args = {k:v for k,v in args.items() if k in valid}
        try:
            hasil = fungsi(**args)
        except Exception as e:
            hasil = {"status":"error","pesan":str(e)}
        fakta, instruksi = _fakta_dan_instruksi(nama, hasil)
        fakta_semua.append(fakta); instruksi_semua.append(instruksi)

    # Langkah 3: LLM merangkai jawaban dari fakta (panggilan bersih)
    sys_perangkai = (
        "Kamu Oxyra, asisten kualitas udara untuk orang awam. "
        "Tulis jawaban Bahasa Indonesia mengalir, ramah, mudah dipahami. "
        "Pakai HANYA fakta yang diberikan, jangan menambah atau mengarang. "
        "AQI adalah singkatan resmi (Air Quality Index). "
        "Olah jadi kalimat biasa, jangan menyalin label mentah. "
        "Jangan menolak; fakta sudah tersedia, sampaikan dengan ramah. "
    )
    konten = (f"Tolong jawab pertanyaan ini: \"{pertanyaan}\"\n\n"
                f"Fakta yang sudah dipastikan benar:\n{chr(10).join(fakta_semua)}\n\n"
                f"Panduan gaya: {' '.join(instruksi_semua)}")
    r2 = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "stream": False, "options": OPSI_LLM,
        "messages": [{"role":"system","content":sys_perangkai},
                        {"role":"user","content":konten}],
    }, timeout=120)
    return {"reply": _bersihkan(r2.json()["message"].get("content","")),
            "tools_dipakai": tools_dipakai, "model": model,
            "data": " || ".join(fakta_semua)}


if __name__ == "__main__":
    tests = [
        "Negara bagian mana yang ozonnya paling buruk?",       # -> bandingkan_negara_bagian (terburuk)
        "Kota mana di California yang udaranya terburuk?",      # -> bandingkan_county
        "Bagaimana kondisi udara di Los Angeles?",             # -> kondisi_titik
        "Negara bagian mana yang SO2-nya paling tinggi?",      # -> bandingkan_negara_bagian (so2)
        "Bagaimana kondisi CO di Los Angeles?",                # -> kondisi_titik (co)
        "Apa itu ozon?",                                       # -> edukatif
        "Bagaimana kualitas udara di Jakarta?",                # -> wilayah tak ada -> arahkan jujur
    ]
    for t in tests:
        print(f"\n{'='*60}\nQ: {t}")
        h = chat(t)
        print(f"Tools: {h['tools_dipakai']}")
        print(f"Jawaban: {h['reply']}")