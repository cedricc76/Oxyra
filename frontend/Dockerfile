# PELETAKAN: di DALAM folder oxyra-chatbot-page/, nama file "Dockerfile"

# ── Stage 1: build Vite ──
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# PENTING: base URL API di kode frontend harus RELATIF:
#   IQAIR  → fetch("/api/iqair/...")
#   USA    → fetch("/api/usa/...")
# Jangan http://localhost:8000 — itu tidak akan jalan lewat tunnel.
RUN npm run build

# ── Stage 2: serve static ──
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
RUN printf 'server {\n  listen 80;\n  root /usr/share/nginx/html;\n  location / { try_files $uri /index.html; }\n}\n' \
    > /etc/nginx/conf.d/default.conf
EXPOSE 80
