// src/pages/Chat.tsx — chart support + dua subsistem (Jatim & USA)
// Pemilihan subsistem lewat dropdown di baris input.
import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Send, Wind, ChevronDown } from 'lucide-react';
import { DashboardHeader } from '../components/DashboardHeader';
import { useAuth } from '../contexts/AuthContext';
import { OxyraChart } from '../components/OxyraChart';
import { sendMessageToOxyra, type Subsystem } from '../api/oxyra';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  chart?: any;
}

const GREETINGS: Record<Subsystem, string> = {
  jatim: `Saya OXYRA, asisten informasi kualitas udara real-time Jawa Timur.\n\nSaat ini saya memantau 16 kota di Jawa Timur. Anda bisa tanya tentang:\n- Kondisi udara terkini di kota tertentu (Surabaya, Malang, Gresik, dll)\n- Kota mana yang udaranya paling baik atau buruk\n- Kondisi udara Jawa Timur secara keseluruhan\n- Saran aktivitas (olahraga, jalan-jalan) berdasarkan kualitas udara`,
  usa: `Saya OXYRA, asisten informasi kualitas udara historis Amerika Serikat (data US EPA).\n\nCakupan: 53 negara bagian, 4 polutan gas (ozon, NO2, SO2, CO). Anda bisa tanya tentang:\n- Kondisi udara suatu negara bagian atau county\n- Perbandingan antarnegara bagian atau antar-county\n- Lokasi dengan kualitas udara terbaik\n- Pola harian dan tren suatu periode`,
};

export function Chat() {
  const { user } = useAuth();

  const [subsystem, setSubsystem] = useState<Subsystem>('jatim');
  const [model, setModel] = useState('llama3.1:8b');

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `Halo ${user?.fullName || 'there'}! ${GREETINGS['jatim']}`,
      timestamp: new Date(),
    },
  ]);

  const [inputValue, setInputValue] = useState('');
  const [history, setHistory]       = useState<any[]>([]);
  const [loading, setLoading]       = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const gantiSubsystem = (s: Subsystem) => {
    if (s === subsystem) return;
    setSubsystem(s);
    setHistory([]);
    setMessages([
      {
        id: Date.now().toString(),
        type: 'assistant',
        content: `Halo ${user?.fullName || 'there'}! ${GREETINGS[s]}`,
        timestamp: new Date(),
      },
    ]);
  };

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const userText = inputValue;
    setInputValue('');

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    const response = await sendMessageToOxyra(userText, history, subsystem, model);

    setLoading(false);

    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: response.reply,
      timestamp: new Date(),
      chart: response.chart,
    };

    setMessages(prev => [...prev, aiMessage]);
    setHistory(response.history ?? []);
  };

  const quickQuestions = subsystem === 'jatim'
    ? [
        "Bagaimana udara di Surabaya sekarang?",
        "Kota mana di Jawa Timur yang paling buruk?",
        "Apakah aman olahraga di Gresik?",
        "Bagaimana kondisi udara Jawa Timur keseluruhan?",
      ]
    : [
        "Bagaimana kualitas udara di California?",
        "Bandingkan New York dan Texas",
        "Negara bagian mana yang udaranya paling baik?",
        "Bagaimana pola harian ozon di California?",
      ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <DashboardHeader />

      <main className="container mx-auto px-4 pt-24 pb-8 max-w-4xl h-[calc(100vh-6rem)]">
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-800/50 flex flex-col h-full">

          {/* Header */}
          <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg">
                <Wind className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-slate-900 dark:text-white font-semibold">OXYRA Chatbot</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {subsystem === 'jatim'
                    ? 'Asisten Kualitas Udara — Jawa Timur (Real-time)'
                    : 'Asisten Kualitas Udara — Amerika Serikat (Historis US EPA)'}
                </p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map(message => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Chart di bawah bubble assistant */}
                  {message.chart && message.type === 'assistant' && (
                    <div className="w-full mt-2">
                      <OxyraChart chart={message.chart} />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {/* Quick questions saat awal */}
            {messages.length === 1 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInputValue(q)}
                    className="text-xs px-3 py-2 bg-blue-50 dark:bg-slate-800 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-slate-700 rounded-full hover:bg-blue-100 dark:hover:bg-slate-700 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {/* Typing indicator */}
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm"
              >
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div
                      key={i}
                      className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
                OXYRA sedang memproses...
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-200 dark:border-slate-800 p-4">
            <div className="flex gap-2">
              {/* Dropdown subsistem (panah custom, bisa diatur posisinya) */}
              <div className="relative">
                <select
                  value={subsystem}
                  onChange={e => gantiSubsystem(e.target.value as Subsystem)}
                  disabled={loading}
                  title="Pilih subsistem data"
                  style={{ appearance: 'none', WebkitAppearance: 'none', MozAppearance: 'none', paddingLeft: '0.75rem', paddingRight: '2.1rem' }}
                  className="h-full py-3 bg-white border border-slate-300 text-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <option value="jatim">Jawa Timur</option>
                  <option value="usa">USA</option>
                </select>
                <ChevronDown
                  className="w-4 h-4 text-slate-500 pointer-events-none"
                  style={{ position: 'absolute', right: '0.6rem', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>

              {/* Dropdown model LLM */}
              <div className="relative">
                <select
                  value={model}
                  onChange={e => setModel(e.target.value)}
                  disabled={loading}
                  title="Pilih model LLM"
                  style={{ appearance: 'none', WebkitAppearance: 'none', MozAppearance: 'none', paddingLeft: '0.75rem', paddingRight: '2.1rem' }}
                  className="h-full py-3 bg-white border border-slate-300 text-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <option value="llama3.1:8b">Llama 3.1</option>
                  <option value="qwen3:8b">Qwen3</option>
                </select>
                <ChevronDown
                  className="w-4 h-4 text-slate-500 pointer-events-none"
                  style={{ position: 'absolute', right: '0.6rem', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
              <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder={subsystem === 'jatim' ? 'Tanyakan tentang kualitas udara Jawa Timur...' : 'Tanyakan tentang kualitas udara Amerika Serikat...'}
                disabled={loading}
                className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={loading || !inputValue.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
