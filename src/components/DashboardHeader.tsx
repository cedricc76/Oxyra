import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wind, Moon, Sun, User, LogOut, LayoutDashboard, MessageSquare } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function DashboardHeader() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg shadow-blue-500/30">
              <Wind className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-slate-900 dark:text-white">
                OXYRA
              </h1>
            </div>
          </Link>

          {/* Navigation & Actions */}
          <div className="flex items-center gap-4">
            {/* Navigation Links */}
            <nav className="hidden md:flex items-center gap-2">
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>
              <Link
                to="/chat"
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </Link>
            </nav>

            {/* Theme Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="flex items-center justify-center w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              aria-label="Toggle theme"
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5 text-amber-500" />
              ) : (
                <Moon className="w-5 h-5 text-slate-700" />
              )}
            </button>

            {/* User Menu */}
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="hidden md:block text-sm text-slate-900 dark:text-white">
                  {user?.fullName}
                </span>
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                    <p className="text-sm text-slate-900 dark:text-white">
                      {user?.fullName}
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                      {user?.email}
                    </p>
                  </div>
                  <div className="py-2">
                    <Link
                      to="/profile"
                      className="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <User className="w-4 h-4" />
                      Profil Saya
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Keluar
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}