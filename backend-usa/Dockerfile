# PELETAKAN: di DALAM folder oxyra-v3-usa/, nama file "Dockerfile"

FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Sesuaikan "main:app" dengan entrypoint FastAPI di folder ini
CMD ["uvicorn", "backend_web_usa:app", "--host", "0.0.0.0", "--port", "8000"]
