import httpx
from backend.config import OLLAMA_BASE_URL, REQUEST_TIMEOUT


async def chat(messages: list[dict], model: str) -> str:
    """
    Kirim daftar pesan ke Ollama dan kembalikan teks balasan.
    
    messages: list dict format Ollama, contoh:
        [{"role": "system", "content": "..."},
        {"role": "user",   "content": "..."},
        {"role": "assistant", "content": "..."}]
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"]


async def list_models() -> list[str]:
    """Daftar model yang tersedia di Ollama lokal."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]