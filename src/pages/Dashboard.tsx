// import { Link } from 'react-router-dom';
// import { motion } from 'motion/react';
// import { MessageSquare, Wind, ChevronRight } from 'lucide-react';
// import { useAuth } from '../contexts/AuthContext';
// import { DashboardHeader } from '../components/DashboardHeader';

// export function Dashboard() {
//   const { user } = useAuth();

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
//       <DashboardHeader />

//       <main className="container mx-auto px-4 pt-24 pb-12 max-w-6xl">
//         {/* Welcome Section */}
//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.5 }}
//           className="mb-8"
//         >
//           <h1 className="text-slate-900 dark:text-white mb-2">
//             Selamat Datang, {user?.fullName}!
//           </h1>
//           <p className="text-slate-600 dark:text-slate-400">
//             Mari pantau kualitas udara dan jaga kesehatan Anda hari ini
//           </p>
//         </motion.div>

//         {/* Current Air Quality Card */}
//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.5, delay: 0.1 }}
//           className="mb-8"
//         >
//           <div className="bg-gradient-to-br from-blue-600 to-cyan-500 rounded-2xl shadow-2xl shadow-blue-500/30 p-6 text-white">
//             <div className="flex items-center justify-between mb-4">
//               <div>
//                 <p className="text-blue-100 text-sm mb-1">Kualitas Udara Saat Ini</p>
//                 <h2 className="text-white">Surabaya</h2>
//               </div>
//               <div className="text-right">
//                 <div className="text-4xl tabular-nums">72</div>
//                 <div className="text-sm text-blue-100">AQI</div>
//               </div>
//             </div>
//             <div className="flex items-center justify-between">
//               <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
//                 Sedang
//               </span>
//               <Link
//                 to="/chat"
//                 className="flex items-center gap-2 text-sm hover:underline"
//               >
//                 Lihat Detail
//                 <ChevronRight className="w-4 h-4" />
//               </Link>
//             </div>
//           </div>
//         </motion.div>

//         {/* Quick Action */}
//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.5, delay: 0.2 }}
//         >
//           <Link
//             to="/chat"
//             className="block bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-200/50 dark:border-slate-800/50 p-6 hover:shadow-xl hover:scale-[1.02] transition-all"
//           >
//             <div className="flex items-center justify-between">
//               <div className="flex items-center gap-4">
//                 <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg">
//                   <MessageSquare className="w-6 h-6 text-white" />
//                 </div>
//                 <div>
//                   <h3 className="text-slate-900 dark:text-white">
//                     Mulai Chat dengan OXYRA
//                   </h3>
//                   <p className="text-sm text-slate-600 dark:text-slate-400">
//                     Tanyakan apa saja tentang kualitas udara
//                   </p>
//                 </div>
//               </div>
//               <ChevronRight className="w-6 h-6 text-slate-400" />
//             </div>
//           </Link>
//         </motion.div>
//       </main>
//     </div>
//   );
// }


import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { MessageSquare, Wind, ChevronRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DashboardHeader } from '../components/DashboardHeader';
import { useEffect, useState } from 'react';

// 🔥 Tambahkan interface untuk AQI
interface AqiResponse {
  location: string;
  aqi: number;
  interpretation: string;
  pm25: number;
  pm10: number;
  co: number;
  no2: number;
  o3: number;
  so2: number;
}

export function Dashboard() {
  const { user } = useAuth();

  // 🔥 State untuk AQI
  const [aqiData, setAqiData] = useState<AqiResponse | null>(null);
  const [loading, setLoading] = useState(true);

// Helper untuk kapital huruf pertama
const capitalize = (str: string) =>
  str.charAt(0).toUpperCase() + str.slice(1);

// Interpretasi singkat (ambil sebelum tanda "—")
const shortInterpretation = aqiData?.interpretation
  ? aqiData.interpretation.split("—")[0].trim()
  : "";

  // 🔥 Ambil data AQI dari FastAPI
  useEffect(() => {
  async function fetchAqi() {
    try {
      const res = await fetch('API_BASE_URL');
      const data = await res.json();

      console.log("=== DATA DARI API ===", data);   // ⬅⬅⬅ Tambahkan ini

      setAqiData(data);
    } catch (err) {
      console.error("Gagal mengambil AQI:", err);
    } finally {
      setLoading(false);
    }
  }

  fetchAqi();
}, []);

  useEffect(() => {
    async function fetchAqi() {
      try {
        const res = await fetch('');
        const data = await res.json();
        setAqiData(data);
      } catch (err) {
        console.error("Gagal mengambil data AQI:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchAqi();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <DashboardHeader />

      <main className="container mx-auto px-4 pt-24 pb-12 max-w-6xl">

        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-slate-900 dark:text-white mb-2">
            Selamat Datang, {user?.fullName}!
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Mari pantau kualitas udara dan jaga kesehatan Anda hari ini
          </p>
        </motion.div>

        {/* Current Air Quality Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-br from-blue-600 to-cyan-500 rounded-2xl shadow-2xl shadow-blue-500/30 p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-blue-100 text-sm mb-1">
                  Kualitas Udara Saat Ini
                </p>

                {/* 🔥 Mengambil lokasi dari API */}
                <h2 className="text-white">
                  {/* {aqiData ? aqiData.location.toUpperCase() : "Surabaya"} */}{aqiData ? capitalize(aqiData.location) : "Surabaya"}

                </h2>
              </div>

              <div className="text-right">

                {/* 🔥 Menampilkan AQI real atau loading */}
                <div className="text-4xl tabular-nums">
                  {loading ? "..." : aqiData?.aqi ?? "--"}
                </div>

                <div className="text-sm text-blue-100">AQI</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              
              {/* 🔥 Menampilkan interpretasi real */}
              <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
                {/* {loading ? "Mengambil data..." : aqiData?.interpretation ?? "Tidak diketahui"} */}{loading ? "Mengambil data..." : capitalize(shortInterpretation) ?? "Tidak diketahui"}

              </span>

              <Link to="/chat" className="flex items-center gap-2 text-sm hover:underline">
                Lihat Detail
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Quick Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Link
            to="/chat"
            className="block bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-200/50 dark:border-slate-800/50 p-6 hover:shadow-xl hover:scale-[1.02] transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-slate-900 dark:text-white">
                    Mulai Chat dengan OXYRA
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Tanyakan apa saja tentang kualitas udara
                  </p>
                </div>
              </div>
              <ChevronRight className="w-6 h-6 text-slate-400" />
            </div>
          </Link>
        </motion.div>
      </main>
    </div>
  );
}
