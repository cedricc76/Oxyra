# PELETAKAN: di DALAM folder oxyra-v3-iqair/, nama file "Dockerfile"

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Sesuaikan "main:app" dengan nama file & variabel FastAPI di folder ini
# (mis. chat_jatim:app jika entrypoint-nya chat_jatim.py)
CMD ["uvicorn", "backend_web:app", "--host", "0.0.0.0", "--port", "8000"]
