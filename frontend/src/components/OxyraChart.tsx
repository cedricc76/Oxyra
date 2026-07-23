// src/components/OxyraChart.tsx
// Komponen chart universal — render Bar, Line, atau Heatmap
// berdasarkan chart_type dari backend

import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Cell
} from "recharts";

interface ChartData {
  chart_type: "bar" | "line" | "heatmap";
  title: string;
  x_key: string;
  y_keys: string[];
  y_labels: string[];
  colors: string[];
  data: Record<string, any>[];
  description?: string;
}

interface Props {
  chart: ChartData;
}

// Warna AQI untuk heatmap
const AQI_COLORS: Record<number, string> = {
  1: "#22c55e",  // Baik - hijau
  2: "#eab308",  // Sedang - kuning
  3: "#f97316",  // Tidak sehat sensitif - orange
  4: "#ef4444",  // Tidak sehat - merah
  5: "#a855f7",  // Sangat tidak sehat - ungu
};

function getAqiColor(aqi: number): string {
  return AQI_COLORS[aqi] || "#94a3b8";
}

// ── Bar Chart ──────────────────────────────────────────────────
function OxyraBarChart({ chart }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey={chart.x_key}
          tick={{ fill: "#64748b", fontSize: 11 }}
          angle={-35}
          textAnchor="end"
          interval={0}
        />
        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            color: "#0f172a",
          }}
        />
        <Legend wrapperStyle={{ color: "#94a3b8", paddingTop: "20px" }} />
        {chart.y_keys.map((key, i) => (
          <Bar
            key={key}
            dataKey={key}
            name={chart.y_labels[i] || key}
            fill={chart.colors[i] || "#3b82f6"}
            radius={[4, 4, 0, 0]}
          >
            {chart.chart_type === "bar" && key === "avg_aqi" &&
              chart.data.map((entry, index) => (
                <Cell key={index} fill={getAqiColor(Math.round(entry[key]))} />
              ))
            }
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Line Chart ─────────────────────────────────────────────────
function OxyraLineChart({ chart }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey={chart.x_key}
          tick={{ fill: "#64748b", fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            color: "#0f172a",
          }}
        />
        <Legend wrapperStyle={{ color: "#94a3b8" }} />
        {chart.y_keys.map((key, i) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={chart.y_labels[i] || key}
            stroke={chart.colors[i] || "#0ea5e9"}
            strokeWidth={2}
            dot={{ r: 4, fill: chart.colors[i] || "#0ea5e9" }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

// ── Heatmap (pakai Bar dengan warna dinamis) ───────────────────
function OxyraHeatmap({ chart }: Props) {
  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-1 justify-start">
        {chart.data.map((item, i) => {
          const aqi = item["aqi"] || 1;
          const color = getAqiColor(aqi);
          return (
            <div
              key={i}
              className="flex flex-col items-center justify-center rounded-lg p-2 min-w-[60px]"
              style={{ backgroundColor: color + "33", border: `1px solid ${color}` }}
              title={`${item[chart.x_key]}: AQI ${aqi}`}
            >
              <span className="text-xs text-slate-700">{item[chart.x_key]}</span>
              <span className="text-sm font-bold" style={{ color }}>
                {aqi}
              </span>
            </div>
          );
        })}
      </div>
      {/* Legend */}
      <div className="flex gap-3 mt-3 flex-wrap">
        {[
          { aqi: 1, label: "Baik" },
          { aqi: 2, label: "Sedang" },
          { aqi: 3, label: "Tdk Sehat Sensitif" },
          { aqi: 4, label: "Tdk Sehat" },
          { aqi: 5, label: "Sangat Tdk Sehat" },
        ].map(({ aqi, label }) => (
          <div key={aqi} className="flex items-center gap-1">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: getAqiColor(aqi) }}
            />
            <span className="text-xs text-slate-600">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Export ────────────────────────────────────────────────
export function OxyraChart({ chart }: Props) {
  if (!chart || !chart.data || chart.data.length === 0) return null;

  return (
    <div className="mt-3 p-4 bg-white border border-slate-200 shadow-sm rounded-xl">
      <h3 className="text-sm font-semibold text-slate-700 mb-3">
        📊 {chart.title}
      </h3>

      {chart.chart_type === "bar"     && <OxyraBarChart chart={chart} />}
      {chart.chart_type === "line"    && <OxyraLineChart chart={chart} />}
      {chart.chart_type === "heatmap" && <OxyraHeatmap chart={chart} />}

      <p className="text-xs text-slate-500 mt-2">{chart.description}</p>
    </div>
  );
}