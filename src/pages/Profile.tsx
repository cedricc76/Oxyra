import { useState, FormEvent } from 'react';
import { motion } from 'motion/react';
import { User, Mail, Calendar, Loader2, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DashboardHeader } from '../components/DashboardHeader';

export function Profile() {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.fullName || '');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setSuccessMessage('');

    try {
      await updateProfile({ fullName });
      setSuccessMessage('Profil berhasil diperbarui!');
      setIsEditing(false);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <DashboardHeader />

      <main className="container mx-auto px-4 pt-24 pb-12 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-slate-900 dark:text-white mb-8">
            Profil Pengguna
          </h1>

          {/* Profile Card */}
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-800/50 overflow-hidden">
            {/* Header with Avatar */}
            <div className="bg-gradient-to-br from-blue-600 to-cyan-500 px-8 py-12 text-center">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white/20 backdrop-blur-sm border-4 border-white/30 mb-4">
                <User className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-white mb-1">
                {user?.fullName}
              </h2>
              <p className="text-blue-100">{user?.email}</p>
            </div>

            {/* Profile Information */}
            <div className="p-8">
              {successMessage && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl flex items-center gap-3"
                >
                  <Check className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  <p className="text-sm text-emerald-600 dark:text-emerald-400">
                    {successMessage}
                  </p>
                </motion.div>
              )}

              {isEditing ? (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="fullName" className="block text-sm text-slate-700 dark:text-slate-300 mb-2">
                      Nama Lengkap
                    </label>
                    <input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                      className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 disabled:from-slate-400 disabled:to-slate-400 text-white rounded-xl shadow-lg shadow-blue-500/30 disabled:shadow-none transition-all flex items-center justify-center gap-2"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Menyimpan...
                        </>
                      ) : (
                        'Simpan Perubahan'
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setIsEditing(false);
                        setFullName(user?.fullName || '');
                      }}
                      className="px-6 py-3 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-slate-100 rounded-xl transition-all"
                    >
                      Batal
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex items-start gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                        <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                          Nama Lengkap
                        </p>
                        <p className="text-slate-900 dark:text-slate-100">
                          {user?.fullName}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                        <Mail className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                          Email
                        </p>
                        <p className="text-slate-900 dark:text-slate-100">
                          {user?.email}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
                        <Calendar className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                          Tanggal Bergabung
                        </p>
                        <p className="text-slate-900 dark:text-slate-100">
                          {user?.createdAt.toLocaleDateString('id-ID', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                          })}
                        </p>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setIsEditing(true)}
                    className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-lg shadow-blue-500/30 transition-all"
                  >
                    Edit Profil
                  </button>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
