"""Backend web lokal OXYRA USA (US EPA) — satu pintu untuk frontend.
- POST /chat : chatbot (pakai Ollama lokal via chat_engine_usa.chat)
Jalankan dari folder backend USA (dengan .venv aktif):
    uvicorn backend_web_usa:app --host 0.0.0.0 --port 8001 --reload

Pola meniru backend_web.py milik subsistem Jawa Timur.
Logika chatbot TIDAK diubah — file ini hanya membungkus chat_engine_usa.chat
agar dapat diakses frontend melalui HTTP.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# impor logika chatbot yang sudah ada (jangan tulis ulang)
from chat_engine_usa import chat as chat_usa

app = FastAPI(title="OXYRA Web Backend USA (lokal)")

# izinkan frontend (Vite biasanya :5173) akses
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                    allow_methods=["*"], allow_headers=["*"])


class ChatReq(BaseModel):
    message: str
    model: str = "llama3.1:8b"


@app.get("/")
def root():
    return {"status": "ok",
            "info": "OXYRA web backend USA lokal. POST /chat"}


@app.post("/chat")
def chat_endpoint(req: ChatReq):
    """Terima pertanyaan dari frontend, jawab via chatbot USA (Ollama lokal)."""
    pesan = (req.message or "").strip()
    if not pesan:
        return {"reply": "Silakan tulis pertanyaan tentang kualitas udara Amerika Serikat.",
                "tools_dipakai": [], "chart": None}

    try:
        hasil = chat_usa(pesan, model=req.model)
        return {"reply": hasil.get("reply", "Tidak ada respons."),
                "tools_dipakai": hasil.get("tools_dipakai", []),
                "chart": None}
    except Exception as e:
        return {"reply": f"Maaf, terjadi kendala pada server: {e}",
                "tools_dipakai": [], "chart": None}
