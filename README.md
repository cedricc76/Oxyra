# OXYRA — Air Quality Chatbot (`oxyra`)

Sistem chatbot kualitas udara berbasis **LLM lokal (Ollama)** dengan arsitektur *tool-calling* anti-halusinasi: chatbot hanya menjawab dari data terverifikasi, bukan dari "ingatan" model. Mencakup dua domain — **Jawa Timur (real-time, IQAir, 16 kota)** dan **Amerika Serikat (historis US EPA, 53 negara bagian, 4 polutan)** — disajikan melalui web frontend (dashboard, grafik interaktif, chat) dan berjalan sepenuhnya di **Docker Compose**. Produksi berjalan di VM GPU (2× RTX 5070 Ti) dan diakses publik via **Cloudflare Tunnel**.

> Tugas Akhir — Teknik Komputer, Institut Teknologi Sepuluh Nopember (ITS), Surabaya.

---

## 🚀 Fitur Utama

- **Dual-domain chatbot**: Jawa Timur (real-time) & USA (historis EPA), masing-masing dengan tools datanya sendiri.
- **Anti-halusinasi via tool-calling**: model wajib memanggil tool data (CSV/SQL) sebelum menjawab; pertanyaan di luar cakupan data ditolak secara eksplisit.
- **Dukungan multi-model**: `llama3.1:8b` (default) dan `qwen3:8b` via Ollama — dapat dipilih dari UI untuk perbandingan.
- **Data pipeline otomatis**: collector mengambil data 16 kota Jawa Timur dari IQAir tiap 2 jam (slot menit 00 WIB) ke volume persisten.
- **Visualisasi interaktif**: dashboard AQI, bar chart perbandingan kota, line chart tren harian.
- **RAG pengetahuan statis**: penjelasan polutan & saran kesehatan via embedding `nomic-embed-text`.
- **Model resident di VRAM** (`OLLAMA_KEEP_ALIVE=-1`) — tanpa cold start.
- **Akses publik tanpa IP publik**: Cloudflare Tunnel (protokol HTTP/2).

---

## 📁 Struktur Proyek

```text
Oxyra/
├── backend-jatim/
│   ├── backend_web.py        # FastAPI chatbot Jawa Timur (/chat, /chart/*)
│   ├── chat_jatim.py         # Engine chat + loop tool-calling
│   ├── tools_jatim.py        # Tools data Jatim (terbaru, per-kota, tren)
│   ├── api_jatim.py          # API penyaji CSV (terbaru, kota, semua)
│   ├── collector_jatim.py    # Collector IQAir, scheduler slot 2 jam WIB
│   └── Dockerfile
├── backend-usa/
│   ├── backend_web_usa.py    # FastAPI chatbot USA (/chat)
│   ├── chat_engine_usa.py    # Engine chat + tool-calling
│   ├── tools_usa.py          # Tools query MariaDB (multi-polutan, 3 tingkat)
│   ├── rag.py                # Build & pencarian indeks RAG
│   ├── pengetahuan_udara.py  # Sumber pengetahuan statis
│   ├── scripts/              # Import dataset EPA (sekali pakai)
│   └── Dockerfile
├── frontend/                 # Vite + React (dashboard, grafik, chat)
├── docs/                     # SOP & dokumentasi tambahan
├── docker-compose.yml        # 9 service + profiles tunnel (quick/named)
├── nginx.conf                # Reverse proxy: / → FE, /api/iqair, /api/usa
├── .env.example              # Templat konfigurasi
├── README-LOKAL.md           # Panduan menjalankan di komputer lokal
└── README.md
```

---

## 🛠️ Persyaratan Sistem

- **Docker** Engine + Compose v2 (atau Docker Desktop)
- **RAM**: ≥16 GB (inferensi CPU) — **GPU NVIDIA** ≥12 GB VRAM disarankan
- **Disk**: ±25 GB (image + model ±11 GB + database)
- **GPU di container**: `nvidia-container-toolkit` + spec CDI (lihat §Deploy GPU)
- **API key IQAir** (Community, gratis) — pengambilan data Jatim
- Berkas data (di luar repo, minta ke pemilik): `dump_utf8.sql` (DB EPA ±700 MB), `historical_jatim.csv` (riwayat Jatim, opsional)

---

## ⚙️ Variabel Lingkungan (`.env`)

Salin dari templat: `cp .env.example .env`

```env
# API key IQAir Community — https://dashboard.iqair.com
IQAIR_API_KEY=your_iqair_api_key

# Token Cloudflare Tunnel (kosongkan untuk pemakaian lokal)
TUNNEL_TOKEN=
```

---

## 💻 Cara Memulai

### 1. Siapkan model & data (sekali saja)

```bash
docker compose up -d ollama mysql
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull qwen3:8b
docker compose exec ollama ollama pull nomic-embed-text

# Database USA
docker cp dump_utf8.sql oxyra-mysql:/tmp/
docker compose exec mysql sh -c "mariadb -u root oxyra_v3 < /tmp/dump_utf8.sql"

# Riwayat Jatim (opsional)
docker compose up -d api-jatim
docker cp historical_jatim.csv oxyra-api-jatim:/app/data/historical_jatim.csv
```

### 2. Jalankan seluruh stack

```bash
docker compose up -d --build              # lokal → http://localhost:8080
docker compose --profile quick up -d      # + tunnel URL acak (trycloudflare.com)
docker compose --profile named up -d      # + tunnel domain sendiri (TUNNEL_TOKEN)
```

Panduan lokal lengkap (termasuk tanpa GPU): **`README-LOKAL.md`**.

### 3. Deploy GPU (produksi)

```bash
apt-get install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
systemctl restart docker
apt-mark hold $(dpkg -l | awk '/^ii.*nvidia/{print $2}')   # cegah auto-update merusak driver
```

---

## 📡 API Endpoint

### `POST /api/iqair/chat` — Chatbot Jawa Timur
### `POST /api/usa/chat` — Chatbot USA

#### Request Body Example

```json
{
  "message": "Bagaimana kualitas udara di Surabaya sekarang?",
  "model": "llama3.1:8b"
}
```

#### Supported Models
- `llama3.1:8b` *(default)*
- `qwen3:8b`

### Endpoint data

| Endpoint | Fungsi |
|---|---|
| `GET /api/iqair/terbaru` | Data terbaru 16 kota |
| `GET /api/iqair/kota/{nama}` | Terbaru + riwayat satu kota |
| `GET /api/iqair/chart/areas` | Data bar chart perbandingan |
| `GET /api/iqair/chart/trend/{kota}` | Data line chart tren |

---

## 🔧 Troubleshooting Singkat

| Gejala | Solusi |
|---|---|
| 502 dari proxy | `docker compose restart proxy` |
| Tunnel gagal (`quic timeout`) | flag `--protocol http2` pada cloudflared |
| Import dump: error `ASCII '\0'` | dump ber-encoding UTF-16 → `iconv -f UTF-16LE -t UTF-8` |
| `NVML: Driver/library version mismatch` | `reboot`, lalu `apt-mark hold` paket nvidia |
| Container: `No devices were found` | regenerate CDI → restart docker → **recreate** container |
| Chat lambat | pastikan `OLLAMA_KEEP_ALIVE=-1`, indeks DB, dan payload tool ringkas |

Daftar lengkap + penjelasan: bagian Troubleshooting di dokumentasi `docs/`.

---

## 📚 Dokumentasi Terkait

- `README-LOKAL.md` — menjalankan di komputer lokal (termasuk tanpa GPU)
- `docs/SOP-Pengayaan-Jawaban.md` — SOP menambah data, pengetahuan (RAG), dan integrasi web browsing

---

## 🔗 Lisensi & Atribusi

Proyek Tugas Akhir — **OXYRA**, Teknik Komputer ITS Surabaya.
Sumber data: [IQAir](https://www.iqair.com) (Jawa Timur, real-time) · [US EPA](https://www.epa.gov) (Amerika Serikat, historis).
