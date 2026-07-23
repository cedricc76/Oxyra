"""Chat engine real-time Jawa Timur. LLM pilih tool, KODE ambil data dari API VPS,
LLM rangkai jawaban untuk awam.

ANTI-HALUSINASI (berlapis):
- Input majemuk DIPECAH jadi sub-pertanyaan (Opsi C). Tiap bagian diklasifikasi:
    JAWAB (dalam lingkup) / TOLAK (di luar lingkup) / TANYA (lokasi tak spesifik).
    Bagian yang bisa dijawab tetap diproses; hanya bagian bermasalah yang ditolak/ditanya.
    Hasil digabung jadi SATU paragraf mengalir.
- Gerbang luar-lingkup: oksigen, mikrogram, persen, IPU, prediksi, dalam ruang, virus,
    alergen, kebijakan/tata ruang -> tidak diproses LLM (cegah halusinasi angka/fakta).
- Lokasi tak spesifik ("daerahku","disini") -> minta nama kota, tak mengarang.
- Data tool gagal -> tak melanjutkan kondisi karangan.
"""
import httpx, json, re
import os
from tools_jatim import kondisi_semua_kota, kondisi_kota, peringkat_kota, pola_kota

OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")
OPSI = {"temperature": 0.2, "seed": 42}

LUAR_LINGKUP = [
    "oksigen", "kadar o2", "ug/m", "mikrogram", "mikro gram",
    "persen polusi", "persentase polusi", "persen kadar", "persentase kadar",
    "berapa persen", "ipu", "indeks pencemaran",
    "virus", "bakteri", "kuman", "bibit penyakit", "menular", "alergen",
    "kandungan gas", "zat kimia", "senyawa",
    "2030", "2027", "2028", "2029", "akan datang",
    "dalam ruang", "dalam ruangan", "kamar kos", "sirkulasi udara", "ventilasi",
    "indoor", "di dalam kamar",
    "ditata", "peruntukan", "kawasan hunian", "kawasan industri", "tata ruang",
    "kebijakan", "regulasi", "peraturan pemerintah", "rtrw", "penataan kawasan",
]
LOKASI_TAK_SPESIFIK = [
    "daerahku", "daerah ku", "daerahmu", "daerah mu", "disini", "di sini",
    "tempat saya", "tempatku", "tempat ku", "lokasi saya", "lokasiku", "lokasi ku",
    "sekitar sini", "sekitar saya", "area saya", "daerah saya", "daerah sini",
    "wilayah saya", "kota saya", "tempat tinggal saya", "di sekitar saya",
]

# Kata yang menandakan pertanyaan soal POLA WAKTU / "kapan/jam berapa/besok"
# -> diarahkan ke analisa pola historis (bukan ditolak, bukan ramalan).
POLA_WAKTU = [
    "jam berapa", "kapan", "waktu terbaik", "waktu yang", "pukul berapa",
    "besok", "nanti", "pagi", "siang", "sore", "malam", "subuh", "dini hari",
    "pola", "tren", "kecenderungan", "biasanya", "membaik", "memburuk",
]
PERIODE_KATA = {
    "subuh": "subuh", "dini hari": "subuh", "pagi": "pagi", "siang": "siang",
    "sore": "sore", "malam": "malam",
}
import re as _re
def _deteksi_pola(pertanyaan):
    """Return (is_pola, periode, jam) bila pertanyaan soal pola waktu."""
    q = pertanyaan.lower()
    is_pola = any(k in q for k in POLA_WAKTU)
    periode = None
    for kata, p in PERIODE_KATA.items():
        if kata in q:
            periode = p
            break
    jam = None
    m = _re.search(r"jam\s*(\d{1,2})", q)
    if m:
        j = int(m.group(1))
        # "jam 8 pagi" vs "jam 8 malam" - sederhana: jika 'malam/sore' & jam<12 -> +12
        if j < 12 and ("malam" in q or "sore" in q):
            j += 12
        if 0 <= j <= 23:
            jam = j
    return is_pola, periode, jam

PENOLAKAN = (
    "Halo! Maaf, untuk hal itu saya belum bisa membantu. Saya Oxyra, asisten kualitas "
    "udara Jawa Timur, dan data saya terbatas pada KONDISI TERKINI kualitas udara per kota "
    "(indeks kualitas udara/AQI, polutan dominan, suhu, kelembaban) - bukan kadar oksigen, "
    "konsentrasi mikrogram, persentase polusi, prediksi masa depan, kebijakan tata ruang, "
    "maupun kualitas udara di dalam ruangan. Yang bisa saya bantu, misalnya: \"bagaimana "
    "udara Surabaya sekarang?\", \"kota mana yang paling buruk?\", atau \"aman tidak "
    "olahraga di luar sekarang?\"."
)
TANYA_KOTA = (
    "Boleh sebutkan kota atau daerah di Jawa Timur yang ingin Anda tanyakan? Saya butuh "
    "nama kotanya untuk memberi info yang tepat - misalnya Surabaya, Malang, Gresik, atau "
    "Sidoarjo. Atau kalau mau, saya bisa tampilkan gambaran seluruh Jawa Timur."
)

def _pecah_pertanyaan(teks):
    """Pecah input majemuk jadi sub-pertanyaan (per baris, penomoran, tanda tanya)."""
    t = teks.strip().strip('"').strip()
    out = []
    for b in re.split(r'[\n\r]+', t):
        b = re.sub(r'^\s*(?:\d+[\.\)]|[-\u2022])\s*', '', b.strip().strip('"').strip())
        sub = re.findall(r'[^?]*\?', b)
        sisa = re.sub(r'[^?]*\?', '', b).strip()
        for p in (sub + [sisa] if sub else [b]):
            p = p.strip().strip('"').strip()
            if len(p) >= 4:
                out.append(p)
    return out or [teks.strip()]

def _klasifikasi(q):
    ql = q.lower()
    is_pola, _, _ = _deteksi_pola(q)
    # Pertanyaan soal POLA WAKTU (kapan/jam berapa/besok) -> JAWAB via pola_kota,
    # KECUALI juga menyentuh data yang benar-benar tak dimiliki (oksigen, dsb).
    if is_pola and not any(k in ql for k in LUAR_LINGKUP):
        return "JAWAB"
    if any(k in ql for k in LUAR_LINGKUP):
        return "TOLAK"
    if any(k in ql for k in LOKASI_TAK_SPESIFIK):
        return "TANYA"
    return "JAWAB"

TOOLS_SCHEMA = [
    {"type":"function","function":{
        "name":"kondisi_semua_kota",
        "description":"Kondisi kualitas udara terkini SEMUA kota di Jawa Timur. Untuk 'bagaimana udara Jawa Timur', 'kondisi semua kota'.",
        "parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{
        "name":"kondisi_kota",
        "description":"Kondisi kualitas udara terkini SATU kota di Jawa Timur. Untuk 'udara di Surabaya', 'AQI Malang sekarang'.",
        "parameters":{"type":"object","properties":{
            "nama":{"type":"string","description":"nama kota, mis. Surabaya, Malang, Gresik"}
        },"required":["nama"]}}},
    {"type":"function","function":{
        "name":"peringkat_kota",
        "description":"Peringkat kota Jatim dari kualitas udara terburuk atau terbaik. Untuk 'kota mana paling buruk/bersih di Jatim'.",
        "parameters":{"type":"object","properties":{
            "urutan":{"type":"string","enum":["terburuk","terbaik"]}
        }}}},
    {"type":"function","function":{
        "name":"pola_kota",
        "description":"Pola/tren historis kualitas udara satu kota Jatim (jam/periode biasanya terbaik-terburuk, arah membaik/memburuk). Untuk 'jam berapa biasanya udara terbaik', 'kapan waktu baik olahraga', 'membaik atau memburuk', atau pertanyaan 'besok' yang dijawab sebagai gambaran pola (bukan ramalan).",
        "parameters":{"type":"object","properties":{
            "nama":{"type":"string","description":"nama kota, mis. Surabaya, Malang"},
            "periode_diminta":{"type":"string","description":"opsional: subuh/pagi/siang/sore/malam bila user sebut"},
            "jam_diminta":{"type":"integer","description":"opsional: jam 0-23 bila user sebut jam spesifik"}
        },"required":["nama"]}}},
]
FUNGSI = {"kondisi_semua_kota": kondisi_semua_kota,
            "kondisi_kota": kondisi_kota,
            "peringkat_kota": peringkat_kota,
            "pola_kota": pola_kota}

SYSTEM = """Kamu Oxyra, asisten kualitas udara real-time untuk Jawa Timur.
Untuk pertanyaan kondisi udara kota/wilayah Jatim, pilih tool yang tepat.
Bahasa Indonesia sederhana & ramah. Jangan sebut kata 'tool' atau proses internalmu."""

DISCLAIMER = ("\n\nCatatan: angka/kondisi di atas adalah indikasi skala kota "
            "(satu titik pantau per kota) dan tidak menggantikan data pemantauan "
            "lokal resmi seperti stasiun DLH/KLH atau sensor di sekitar lokasi Anda.")

def _ambil_fakta(pertanyaan_gabungan, model, periode=None, jam=None):
    """Panggil LLM untuk pilih tool, jalankan, kembalikan (list fakta, tools, semua_gagal).
    periode/jam: hasil deteksi deterministik dari kode; disuntikkan ke pola_kota bila dipanggil."""
    r = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "tools": TOOLS_SCHEMA, "stream": False, "options": OPSI,
        "messages":[{"role":"system","content":SYSTEM},
                    {"role":"user","content":pertanyaan_gabungan}]}, timeout=120)
    calls = r.json()["message"].get("tool_calls", [])
    if not calls:
        return None, [], False
    fakta, dipakai = [], []
    for tc in calls:
        nama = tc["function"]["name"]
        args = dict(tc["function"].get("arguments", {}))
        print(f"  [debug] {nama} args: {args}")
        if nama not in FUNGSI:
            continue
        valid = FUNGSI[nama].__code__.co_varnames[:FUNGSI[nama].__code__.co_argcount]
        args = {k:v for k,v in args.items() if k in valid}
        # Periode/jam DITENTUKAN KODE, bukan LLM (buang tebakan LLM yang sering salah).
        if nama == "pola_kota":
            args.pop("periode_diminta", None)
            args.pop("jam_diminta", None)
            if periode is not None:
                args["periode_diminta"] = periode
            if jam is not None:
                args["jam_diminta"] = jam
        hasil = FUNGSI[nama](**args)
        dipakai.append(nama)
        if hasil.get("status") == "ok":
            fakta.append(hasil["ringkas"])
        else:
            fakta.append("[DATA TIDAK DITEMUKAN] " + hasil.get("pesan", "Data tidak tersedia."))
    semua_gagal = bool(fakta) and all(f.startswith("[DATA TIDAK DITEMUKAN]") for f in fakta)
    return fakta, dipakai, semua_gagal

def _jawab_langsung(pertanyaan, model):
    sys_aman = (
        "Kamu Oxyra, asisten kualitas udara Jawa Timur yang ramah. Bahasa Indonesia sederhana. "
        "ATURAN KETAT ANTI-MENGARANG: Kamu HANYA punya data kondisi TERKINI kualitas udara per "
        "kota (indeks AQI, polutan dominan, suhu, kelembaban). Kamu TIDAK punya data lain "
        "(oksigen, mikrogram, persen, IPU, prediksi, dalam ruang, virus, kebijakan). "
        "Jangan mengarang angka/fakta/saran. Jika di luar itu, katakan jujur dan arahkan ke "
        "kondisi udara terkini kota Jatim."
    )
    r = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "stream": False, "options": OPSI,
        "messages":[{"role":"system","content":sys_aman},
                    {"role":"user","content":pertanyaan}]}, timeout=120)
    return r.json()["message"].get("content","")

def chat(pertanyaan, model="llama3.1:8b"):
    # 1) Pecah input jadi sub-pertanyaan
    bagian = _pecah_pertanyaan(pertanyaan)
    kelas = [_klasifikasi(b) for b in bagian]
    print(f"  [debug] {len(bagian)} bagian -> {list(zip([k for k in kelas], [b[:30] for b in bagian]))}")

    yang_dijawab = [b for b, k in zip(bagian, kelas) if k == "JAWAB"]
    ada_tolak = "TOLAK" in kelas
    ada_tanya = "TANYA" in kelas

    # 2) Kalau TIDAK ada yang bisa dijawab -> penolakan/tanya sesuai isi
    if not yang_dijawab:
        if ada_tanya and not ada_tolak:
            print("  [debug] semua bagian butuh nama kota")
            return {"reply": TANYA_KOTA, "tools": [], "data": ""}
        print("  [debug] semua bagian di luar lingkup -> penolakan")
        return {"reply": PENOLAKAN, "tools": [], "data": ""}

    # 3) Ada bagian yang bisa dijawab -> ambil fakta untuk gabungan pertanyaan itu
    gabung_jawab = " ".join(yang_dijawab)
    # Deteksi konteks pola/waktu (periode & jam) dari bagian yang dijawab, untuk pola_kota
    _isp, _periode, _jam = _deteksi_pola(gabung_jawab)
    fakta, dipakai, semua_gagal = _ambil_fakta(gabung_jawab, model, periode=_periode, jam=_jam)

    if fakta is None:
        # LLM tak memanggil tool -> jalur langsung yang dibatasi
        jwb = _jawab_langsung(gabung_jawab, model)
        return {"reply": jwb, "tools": [], "data": ""}
    if semua_gagal:
        print("  [debug] semua tool gagal -> tanya kota")
        return {"reply": TANYA_KOTA, "tools": dipakai, "data": " || ".join(fakta)}

    # 4) Rangkai jadi SATU paragraf mengalir; sisipkan catatan bila ada yg ditolak/ditanya
    catatan = []
    if ada_tolak:
        catatan.append("sebagian hal yang ditanyakan (mis. data yang tidak dimiliki sistem atau "
                        "prediksi masa depan) berada di luar yang bisa saya bantu")
    if ada_tanya:
        catatan.append("untuk pertanyaan yang menyebut 'daerah saya/sekitar sini', mohon sebutkan "
                        "nama kotanya agar bisa saya jawab tepat")
    catatan_txt = ("; ".join(catatan)) if catatan else ""

    sys2 = ("Kamu Oxyra, asisten kualitas udara Jawa Timur untuk orang awam. "
            "Jawab dengan bahasa sehari-hari, ramah, mengalir seperti teman, dalam SATU paragraf. "
            "ATURAN: "
            "1. Default beri KESIMPULAN kondisi udara dalam kata sederhana (segar/cukup baik/"
            "kurang sehat/tidak sehat) plus saran praktis (boleh aktivitas/hati-hati, masker/tidak). "
            "2. Jika user MENANYAKAN ANGKA: ditanya suhu/derajat -> sebut angka suhu & kelembaban; "
            "ditanya AQI/tingkat polusi/index/level berapa -> sebut angka AQI. Jangan menolak angka "
            "yang ADA di fakta bila diminta. "
            "3. Pertanyaan aktivitas (olahraga/jogging/jalan) DAN pertanyaan kesehatan yang dikaitkan udara (mis. batuk, sesak, tenggorokan) WAJAR dan HARUS dijawab. JANGAN PERNAH menolak dengan 'tidak bisa membantu' untuk pertanyaan seperti ini; selalu jawab dengan kondisi udara yang ada. "
            "4. Pakai HANYA fakta yang diberikan; JANGAN mengarang data/angka/saran. "
            "5. DILARANG menyebut data yang tak ada di fakta (oksigen, mikrogram, persen, IPU). "
            "6. Jawab HANYA pertanyaan yang tertulis di 'Pertanyaan user'. "
            "KHUSUS bila fakta berisi 'Pola historis': kamu BOLEH menjawab pertanyaan tentang "
            "'jam/waktu terbaik', 'membaik/memburuk', atau 'besok' TETAPI WAJIB membingkainya "
            "sebagai POLA MASA LALU, bukan ramalan. Awali dengan mengakui kamu tidak bisa "
            "memastikan kondisi nanti/besok, lalu sampaikan pola historisnya sebagai gambaran "
            "(gunakan kata 'biasanya', 'berdasarkan pola beberapa hari terakhir'). "
            "JANGAN menyatakan kondisi masa depan sebagai kepastian. "
            "7. Jika ada 'CATATAN TAMBAHAN', selipkan dengan halus di akhir sebagai satu kalimat "
            "sopan, jangan kaku. "
            "8. Bila user bertanya tentang KESEHATAN/GEJALA (mis. 'kenapa batuk', "
            "'apa efek ke pernapasan') yang dikaitkan udara: WAJIB tetap menjawab dengan "
            "menyampaikan kondisi udara terkini, LALU kamu BOLEH memberi penjelasan "
            "KUALITATIF SINGKAT (maksimal 1-2 kalimat) mengenai kaitan parameter yang KAMU MILIKI "
            "(suhu, kelembaban, kategori kualitas udara, polutan dominan termasuk PM2.5) dengan "
            "kenyamanan pernapasan. Ini informasi umum, bukan diagnosis. "
            "BATAS TEGAS: JANGAN mengarang angka yang tak ada di fakta; JANGAN menyebut penyakit "
            "spesifik; JANGAN memberi saran kesehatan yang TIDAK berhubungan dengan kualitas udara "
            "(mis. cuci tangan, minum air, olahraga teratur, konsultasi dokter, pola makan) - saran "
            "hanya boleh seputar udara (aktivitas luar, masker, memilih waktu/lokasi). "
            "Untuk pertanyaan aktivitas/golf/olahraga yang BUKAN pertanyaan kesehatan, JANGAN "
            "menyelipkan penjelasan kesehatan apa pun. Jawab fokus pada kondisi udara & saran udara saja.")
    # PENTING: kirim HANYA bagian yang boleh dijawab (bukan pertanyaan asli utuh),
    # supaya LLM tidak tergoda menjawab bagian yang sudah ditolak (mis. prediksi besok).
    pertanyaan_dijawab = " ".join(yang_dijawab)
    konten = f"Pertanyaan user: \"{pertanyaan_dijawab}\"\n\nFakta (data real-time):\n" + "\n".join(fakta)

    # Bila pertanyaan menyoal WAKTU DEPAN/POLA dan ada fakta pola historis -> instruksi tegas.
    _isp2, _, _ = _deteksi_pola(pertanyaan_dijawab)
    ada_fakta_pola = any("Pola historis" in f for f in fakta)
    menyoal_masa_depan = any(k in pertanyaan_dijawab.lower()
                                for k in ["besok", "nanti", "kapan", "jam berapa"])
    if _isp2 and ada_fakta_pola and menyoal_masa_depan:
        konten += ("\n\nINSTRUKSI WAJIB: Pertanyaan ini menyangkut waktu nanti/besok/kapan. "
                    "Kamu WAJIB menjawabnya BERDASARKAN 'Pola historis' di atas, BUKAN kondisi "
                    "terkini. Awali dengan kalimat bahwa kamu tidak bisa memastikan kondisi "
                    "besok/nanti, LALU sampaikan pola historisnya (jam/periode yang biasanya "
                    "lebih baik) sebagai gambaran. Gunakan kata 'biasanya' dan 'berdasarkan pola "
                    "beberapa hari terakhir'. DILARANG bilang 'besok bisa saja' atau menyatakan "
                    "kondisi besok sebagai kepastian.")

    if catatan_txt:
        konten += f"\n\nCATATAN TAMBAHAN (selipkan halus di akhir sebagai SATU kalimat sopan): {catatan_txt}."
    r2 = httpx.post(f"{OLLAMA}/api/chat", json={
        "model": model, "stream": False, "options": OPSI,
        "messages":[{"role":"system","content":sys2},
                    {"role":"user","content":konten}]}, timeout=120)
    reply = r2.json()["message"].get("content", "")
    _data_query = " || ".join(fakta)  # data hasil query yang jadi dasar jawaban
    # Buang label kaku bila LLM menyalinnya mentah (kosmetik, deterministik)
    import re as _re2
    reply = _re2.sub(r"\s*CATATAN TAMBAHAN\s*:?\s*", " ", reply, flags=_re2.IGNORECASE).strip()
    return {"reply": reply + DISCLAIMER, "tools": dipakai, "data": _data_query}

if __name__ == "__main__":
    print("="*55)
    print("  OXYRA - Chatbot Kualitas Udara Real-time Jawa Timur")
    print("="*55)
    print("Tanya kondisi udara kota Jawa Timur. Ketik 'keluar' untuk berhenti.")
    print("Contoh: 'udara Surabaya sekarang?', 'kota mana paling buruk?'\n")
    while True:
        try:
            q = input("Anda: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break
        if not q:
            continue
        if q.lower() in ("keluar", "exit", "quit", "selesai"):
            print("Sampai jumpa!")
            break
        h = chat(q)
        print(f"\nOxyra: {h['reply']}\n")