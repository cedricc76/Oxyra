import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const { location } = req.query;

  if (!location || typeof location !== 'string') {
    return res.status(400).json({ error: 'Parameter location wajib diisi' });
  }

  const API_BASE_URL = process.env.VITE_API_BASE_URL;
  if (!API_BASE_URL) {
    return res.status(500).json({ error: 'VITE_API_BASE_URL belum diset di environment' });
  }

  try {
    const upstream = await fetch(`${API_BASE_URL}/aqi/${encodeURIComponent(location)}`);
    
    if (!upstream.ok) {
      const text = await upstream.text().catch(() => '');
      return res.status(upstream.status).json({ error: text });
    }

    const data = await upstream.json();
    return res.status(200).json(data);

  } catch (err: any) {
    return res.status(500).json({ error: err.message });
  }
}