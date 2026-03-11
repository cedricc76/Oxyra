// src/api/base.ts
export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") || "";

export const N8N_BASE_URL =
  (import.meta.env.VITE_N8N_BASE_URL as string | undefined)?.replace(/\/$/, "") || "http://localhost:5678";