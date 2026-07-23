"""Retrieval RAG: cari entri pengetahuan paling relevan dengan pertanyaan.
Dipakai chat_engine untuk menjawab pertanyaan edukatif secara akurat."""
import httpx, json, math
import os

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_EMBED = "nomic-embed-text"
FILE_INDEKS = "indeks_rag.json"
AMBANG = 0.6   # skor minimum agar entri dianggap relevan

# Muat indeks sekali saat modul di-import
with open(FILE_INDEKS, encoding="utf-8") as f:
    _INDEKS = json.load(f)

def _embed(teks: str) -> list:
    r = httpx.post(f"{OLLAMA}/api/embeddings",
                    json={"model": MODEL_EMBED, "prompt": teks}, timeout=120)
    return r.json()["embedding"]

def _cosine(a, b) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0.0

def cari(pertanyaan: str, top_k: int = 2) -> list:
    """Kembalikan top_k entri paling relevan (skor >= AMBANG). Bisa kosong."""
    v_tanya = _embed(f"search_query: {pertanyaan}")
    skor = [(_cosine(v_tanya, e["vektor"]), e) for e in _INDEKS]
    skor.sort(key=lambda x: x[0], reverse=True)
    hasil = [{"topik": e["topik"], "isi": e["isi"], "skor": round(s, 3)}
                for s, e in skor[:top_k] if s >= AMBANG]
    return hasil


if __name__ == "__main__":
    # Tes retrieval dengan beberapa pertanyaan
    tes = [
        "Apa itu AQI dan kategorinya?",
        "Apakah CO sama dengan karbondioksida?",
        "Apakah ozon itu polutan atau pelindung?",
        "Siapa yang paling rentan terhadap polusi?",
        "Resep nasi goreng enak",   # di luar topik -> harusnya kosong/rendah
    ]
    for q in tes:
        print(f"\nQ: {q}")
        hasil = cari(q)
        for h in hasil:
            print(f"  [{h['skor']}] {h['topik']}")
        if not hasil:
            print("  (tidak ada entri relevan)")