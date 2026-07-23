import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Wind, MessageSquare, TrendingUp, Shield, Sparkles, ArrowRight, BarChart3, Brain } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function Landing() {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && user) {
      navigate('/dashboard');
    }
  }, [user, isLoading, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <div className="text-center">
          <Wind className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600 dark:text-slate-400">Memuat...</p>
        </div>
      </div>
    );
  }

  const features = [
    {
      icon: MessageSquare,
      title: 'Data AQI Real-time',
      description: 'Informasi kualitas udara terkini dari satelit',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: TrendingUp,
      title: 'Rekomendasi Aktivitas',
      description: 'Saran aktivitas aman berdasarkan kondisi kualitas udara saat ini',
      color: 'from-emerald-500 to-teal-500',
    },
    {
      icon: Shield,
      title: 'Edukasi Kesehatan',
      description: 'Panduan lengkap tentang dampak polusi udara dan cara perlindungan diri',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Sparkles,
      title: 'Pemahaman Bahasa Alami',
      description: 'Didukung LLM untuk percakapan natural dan responsif',
      color: 'from-orange-500 to-red-500',
    },
  ];

  const technologies = [
    {
      icon: Brain,
      title: 'LLM Orchestration',
      description: 'Multi-model AI dengan routing cerdas',
    },
    {
      icon: BarChart3,
      title: 'RAG Pipeline',
      description: 'Retrieval-augmented untuk konteks akurat',
    },
    {
      icon: MessageSquare,
      title: 'Natural Language',
      description: 'Pemahaman bahasa Indonesia & Inggris',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Logo */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-2xl shadow-blue-500/30 mb-8">
            <Wind className="w-10 h-10 text-white" />
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-6xl text-slate-900 dark:text-white mb-6">
            OXYRA — Sistem Informasi Cerdas Kualitas Udara Berbasis LLM
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-slate-600 dark:text-slate-400 mb-4 max-w-2xl mx-auto">
            Menyederhanakan akses informasi kualitas udara untuk masyarakat Indonesia dengan kekuatan AI
          </p>
          
          <p className="text-sm text-slate-500 dark:text-slate-500 mb-12">
            Chatbot Berbasis Large Language Model untuk Demokratisasi Informasi Kualitas Udara di Indonesia
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              to="/signup"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-2xl shadow-blue-500/30 transition-all"
            >
              <span>Mulai Sekarang</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="px-8 py-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-900 dark:text-white rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 transition-all"
            >
              Masuk
            </Link>
          </div>
        </motion.div>

        {/* Key Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-20"
        >
          <h2 className="text-slate-900 dark:text-white text-center mb-12">
            Fitur Utama
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              >
                <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-xl border border-slate-200/50 dark:border-slate-800/50 p-6 h-full hover:shadow-2xl hover:scale-105 transition-all">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} shadow-lg mb-4`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-slate-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Technology Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="max-w-4xl mx-auto mb-20"
        >
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-800/50 p-8">
            <h2 className="text-slate-900 dark:text-white text-center mb-8">
              Teknologi Canggih
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {technologies.map((tech, index) => (
                <motion.div
                  key={tech.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.7 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 mb-3">
                    <tech.icon className="w-7 h-7 text-blue-600 dark:text-cyan-400" />
                  </div>
                  <h4 className="text-slate-900 dark:text-white mb-2">
                    {tech.title}
                  </h4>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {tech.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.9 }}
          className="text-center"
        >
          <div className="inline-block bg-gradient-to-br from-blue-600 to-cyan-500 rounded-2xl shadow-2xl shadow-blue-500/30 p-8 max-w-2xl">
            <h3 className="text-white mb-4">
              Siap Memantau Kualitas Udara?
            </h3>
            <p className="text-blue-100 mb-6">
              Bergabunglah dengan OXYRA dan dapatkan informasi kualitas udara real-time dengan rekomendasi kesehatan yang personal
            </p>
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 px-8 py-3 bg-white hover:bg-blue-50 text-blue-600 rounded-xl shadow-lg transition-all"
            >
              <span>Daftar Gratis</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Dikembangkan oleh Cedric Anthony Edysa — Teknik Komputer ITS
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
            Didukung oleh data dari US EPA, IQAir, dan OpenWeatherMap
          </p>
        </div>
      </footer>
    </div>
  );
}
