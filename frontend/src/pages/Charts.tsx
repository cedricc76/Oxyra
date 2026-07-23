// src/pages/Charts.tsx
// Halaman khusus untuk visualisasi grafik AQI Surabaya

import { useState, useEffect } from "react";
import { DashboardHeader } from "../components/DashboardHeader";
import { OxyraChart } from "../components/OxyraChart";
import { BarChart2, TrendingUp } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/iqair";

const KOTA_JATIM = [
  "Surabaya", "Malang", "Madiun", "Gresik", "Mojokerto", "Pasuruan",
  "Probolinggo", "Jombang", "Lumajang", "Bojonegoro", "Bangil",
  "Singosari", "Mojosari", "Lamongan", "Tuban"
];

function DisclaimerSkalaKota() {
  return (
    <div className="mt-3 text-xs rounded-lg px-3 py-2"
          style={{ backgroundColor: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }}>
      ⓘ Angka yang disajikan merupakan <b>indikasi kualitas udara skala kota</b> (satu
      titik pantau per kota) dan <b>tidak menggantikan</b> data pemantauan lokal resmi
      seperti stasiun DLH/KLH atau sensor di sekitar lokasi Anda.
    </div>
  );
}

export function Charts() {
  const [activeTab, setActiveTab]     = useState<"area" | "trend">("area");
  const [areaChart, setAreaChart]     = useState<any>(null);
  const [trendChart, setTrendChart]   = useState<any>(null);
  const [selectedCity, setSelectedCity] = useState("Surabaya");
  const [trendDays, setTrendDays]     = useState(7);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState("");

  const headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
  };

  // Fetch area comparison
  const fetchAreaChart = async () => {
    setLoading(true);
    setError("");
    try {
      const res  = await fetch(`${API_BASE}/chart/areas?days=1`, { headers });
      const data = await res.json();
      setAreaChart(data.chart);
    } catch (e) {
      setError("Gagal memuat data perbandingan area.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch trend chart
  const fetchTrendChart = async () => {
    setLoading(true);
    setError("");
    try {
      const res  = await fetch(`${API_BASE}/chart/trend/${encodeURIComponent(selectedCity)}?days=${trendDays}`, { headers });
      const data = await res.json();
      setTrendChart(data.chart);
    } catch (e) {
      setError("Gagal memuat data tren.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "area")   fetchAreaChart();
    if (activeTab === "trend")  fetchTrendChart();
  }, [activeTab, selectedCity, trendDays]);

  const tabs = [
    { id: "area",   label: "Perbandingan Kota",  icon: <BarChart2 className="w-4 h-4" /> },
    { id: "trend",  label: "Tren Harian",         icon: <TrendingUp className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
      <DashboardHeader />

      <main className="container mx-auto px-4 pt-24 pb-8 max-w-5xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900 mb-1">📊 Visualisasi Kualitas Udara</h1>
          <p className="text-slate-600 text-sm">Grafik interaktif data AQI Jawa Timur</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-slate-200 p-1 rounded-xl w-fit">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Controls */}
        <div className="flex gap-3 mb-4 flex-wrap">
          {activeTab !== "area" && (
            <select
              value={selectedCity}
              onChange={e => setSelectedCity(e.target.value)}
              className="px-3 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {KOTA_JATIM.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          )}

          {activeTab === "trend" && (
            <select
              value={trendDays}
              onChange={e => setTrendDays(Number(e.target.value))}
              className="px-3 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={3}>3 Hari</option>
              <option value={7}>7 Hari</option>
              <option value={14}>14 Hari</option>
              <option value={30}>30 Hari</option>
            </select>
          )}

          <button
            onClick={() => {
              if (activeTab === "area")   fetchAreaChart();
              if (activeTab === "trend")  fetchTrendChart();
            }}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-lg text-sm font-medium transition-all"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Chart Container */}
        <div className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6">
          {loading && (
            <div className="flex items-center justify-center h-48 text-slate-500">
              <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mr-2" />
              Memuat data...
            </div>
          )}

          {error && !loading && (
            <div className="text-sm p-4 rounded-lg" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c' }}>{error}</div>
          )}

          {!loading && !error && (
            <>
              {activeTab === "area"   && areaChart   && <OxyraChart chart={areaChart} />}
              {activeTab === "trend"  && trendChart   && <OxyraChart chart={trendChart} />}

              {activeTab === "area"   && !areaChart   && <p className="text-slate-600 text-sm">Belum ada data area.</p>}
              {activeTab === "trend"  && !trendChart   && <p className="text-slate-600 text-sm">Belum ada data tren untuk {selectedCity}.</p>}
            </>
          )}
          <DisclaimerSkalaKota />
        </div>
      </main>
    </div>
  );
}