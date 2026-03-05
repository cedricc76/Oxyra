// import { useState } from 'react';
// import { motion } from 'motion/react';
// import { Send, Wind } from 'lucide-react';
// import { DashboardHeader } from '../components/DashboardHeader';
// import { useAuth } from '../contexts/AuthContext';

// interface Message {
//   id: string;
//   type: 'user' | 'assistant';
//   content: string;
//   timestamp: Date;
// }

// export function Chat() {
//   const { user } = useAuth();
//   const [messages, setMessages] = useState<Message[]>([
//     {
//       id: '1',
//       type: 'assistant',
//       content: `Halo ${user?.fullName || 'there'}! Saya OXYRA, asisten cerdas untuk kualitas udara Indonesia. Saya siap membantu Anda mendapatkan informasi real-time tentang kualitas udara, rekomendasi kesehatan, dan edukasi tentang polusi. Apa yang ingin Anda ketahui hari ini?`,
//       timestamp: new Date(),
//     },
//   ]);
//   const [inputValue, setInputValue] = useState('');

//   const handleSend = () => {
//     if (!inputValue.trim()) return;

//     // Add user message
//     const userMessage: Message = {
//       id: Date.now().toString(),
//       type: 'user',
//       content: inputValue,
//       timestamp: new Date(),
//     };

//     setMessages([...messages, userMessage]);
//     setInputValue('');

//     // Simulate AI response
//     setTimeout(() => {
//       const aiMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         type: 'assistant',
//         content: 'Terima kasih atas pertanyaan Anda! Saya dapat membantu Anda dengan informasi tentang kualitas udara real-time, rekomendasi kesehatan, dampak polusi, dan tips pencegahan.',
//         timestamp: new Date(),
//       };
//       setMessages((prev) => [...prev, aiMessage]);
//     }, 1000);
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
//       <DashboardHeader />

//       <main className="container mx-auto px-4 pt-24 pb-8 max-w-4xl h-[calc(100vh-6rem)]">
//         <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-800/50 flex flex-col h-full">
//           {/* Header */}
//           <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4">
//             <div className="flex items-center gap-3">
//               <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg">
//                 <Wind className="w-6 h-6 text-white" />
//               </div>
//               <div>
//                 <h2 className="text-slate-900 dark:text-white">OXYRA Chatbot</h2>
//                 <p className="text-sm text-slate-600 dark:text-slate-400">Asisten Kualitas Udara</p>
//               </div>
//             </div>
//           </div>

//           {/* Messages */}
//           <div className="flex-1 overflow-y-auto p-6 space-y-4">
//             {messages.map((message) => (
//               <motion.div
//                 key={message.id}
//                 initial={{ opacity: 0, y: 10 }}
//                 animate={{ opacity: 1, y: 0 }}
//                 transition={{ duration: 0.3 }}
//                 className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
//               >
//                 <div
//                   className={`max-w-[80%] rounded-2xl px-4 py-3 ${
//                     message.type === 'user'
//                       ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white'
//                       : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100'
//                   }`}
//                 >
//                   <p className="text-sm whitespace-pre-wrap">{message.content}</p>
//                 </div>
//               </motion.div>
//             ))}
//           </div>

//           {/* Input */}
//           <div className="border-t border-slate-200 dark:border-slate-800 p-4">
//             <div className="flex gap-2">
//               <input
//                 type="text"
//                 value={inputValue}
//                 onChange={(e) => setInputValue(e.target.value)}
//                 onKeyPress={(e) => e.key === 'Enter' && handleSend()}
//                 placeholder="Tanyakan tentang kualitas udara..."
//                 className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
//               />
//               <button
//                 onClick={handleSend}
//                 className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2"
//               >
//                 <Send className="w-5 h-5" />
//               </button>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }


// import { useState } from 'react';
// import { motion } from 'motion/react';
// import { Send, Wind } from 'lucide-react';
// import { DashboardHeader } from '../components/DashboardHeader';
// import { useAuth } from '../contexts/AuthContext';

// // Import API
// import { sendMessageToOxyra } from '../api/oxyra';

// interface Message {
//   id: string;
//   type: 'user' | 'assistant';
//   content: string;
//   timestamp: Date;
// }

// export function Chat() {
//   const { user } = useAuth();
//   const [messages, setMessages] = useState<Message[]>([
//     {
//       id: '1',
//       type: 'assistant',
//       content: `Halo ${user?.fullName || 'there'}! Saya OXYRA, asisten cerdas untuk kualitas udara Indonesia. Apa yang ingin Anda ketahui hari ini?`,
//       timestamp: new Date(),
//     },
//   ]);
  
//   const [inputValue, setInputValue] = useState('');
//   const [history, setHistory] = useState<any[]>([]);
//   const [loading, setLoading] = useState(false);

//   const handleSend = async () => {
//     if (!inputValue.trim()) return;

//     const userText = inputValue;
//     setInputValue('');

//     // Tambah pesan user
//     const userMessage: Message = {
//       id: Date.now().toString(),
//       type: 'user',
//       content: userText,
//       timestamp: new Date(),
//     };

//     setMessages(prev => [...prev, userMessage]);

//     // Tampilkan typing indicator
//     setLoading(true);

//     // Panggil backend FastAPI
//     const response = await sendMessageToOxyra(userText, history);

//     setLoading(false);

//     // Tambah pesan AI
//     const aiMessage: Message = {
//       id: (Date.now() + 1).toString(),
//       type: 'assistant',
//       content: response.reply,
//       timestamp: new Date(),
//     };

//     setMessages(prev => [...prev, aiMessage]);

//     // Update history internal OXYRA
//     setHistory(response.history);
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
//       <DashboardHeader />

//       <main className="container mx-auto px-4 pt-24 pb-8 max-w-4xl h-[calc(100vh-6rem)]">
//         <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-800/50 flex flex-col h-full">

//           {/* Header */}
//           <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4">
//             <div className="flex items-center gap-3">
//               <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg">
//                 <Wind className="w-6 h-6 text-white" />
//               </div>
//               <div>
//                 <h2 className="text-slate-900 dark:text-white">OXYRA Chatbot</h2>
//                 <p className="text-sm text-slate-600 dark:text-slate-400">
//                   Asisten Kualitas Udara
//                 </p>
//               </div>
//             </div>
//           </div>

//           {/* Messages */}
//           <div className="flex-1 overflow-y-auto p-6 space-y-4">
//             {messages.map(message => (
//               <motion.div
//                 key={message.id}
//                 initial={{ opacity: 0, y: 10 }}
//                 animate={{ opacity: 1, y: 0 }}
//                 transition={{ duration: 0.3 }}
//                 className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
//               >
//                 <div
//                   className={`max-w-[80%] rounded-2xl px-4 py-3 ${
//                     message.type === 'user'
//                       ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white'
//                       : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100'
//                   }`}
//                 >
//                   <p className="text-sm whitespace-pre-wrap">{message.content}</p>
//                 </div>
//               </motion.div>
//             ))}

//             {loading && (
//               <motion.div
//                 initial={{ opacity: 0 }}
//                 animate={{ opacity: 1 }}
//                 className="text-slate-600 dark:text-slate-400 text-sm"
//               >
//                 OXYRA sedang memproses...
//               </motion.div>
//             )}
//           </div>

//           {/* Input */}
//           <div className="border-t border-slate-200 dark:border-slate-800 p-4">
//             <div className="flex gap-2">
//               <input
//                 type="text"
//                 value={inputValue}
//                 onChange={e => setInputValue(e.target.value)}
//                 onKeyDown={e => e.key === 'Enter' && handleSend()}
//                 placeholder="Tanyakan tentang kualitas udara..."
//                 className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
//               />
//               <button
//                 onClick={handleSend}
//                 className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2"
//               >
//                 <Send className="w-5 h-5" />
//               </button>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }


import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Send, Wind } from 'lucide-react';
import { DashboardHeader } from '../components/DashboardHeader';
import { useAuth } from '../contexts/AuthContext';

// Import API sender
import { sendMessageToOxyra } from '../api/oxyra';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function Chat() {
  const { user } = useAuth();

  // Pesan yang tampil di UI
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `Halo ${user?.fullName || 'there'}! Saya OXYRA, asisten cerdas untuk kualitas udara Surabaya. Apa yang ingin Anda ketahui hari ini?`,
      timestamp: new Date(),
    },
  ]);

  // Input user
  const [inputValue, setInputValue] = useState('');

  // History internal untuk backend (tidak ditampilkan)
  const [history, setHistory] = useState<any[]>([]);

  // Typing indicator
  const [loading, setLoading] = useState(false);

  // Ref untuk auto-scroll
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Auto scroll setiap ada pesan baru
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Fungsi kirim pesan
  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userText = inputValue;
    setInputValue('');

    // Tambah bubble user
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userText,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // AI typing
    setLoading(true);

    // Kirim ke backend
    const response = await sendMessageToOxyra(userText, history);

    setLoading(false);

    // Tambah bubble AI
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: response.reply,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, aiMessage]);

    // Update history internal OXYRA
    setHistory(response.history);
  };

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
                <h2 className="text-slate-900 dark:text-white">OXYRA Chatbot</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Asisten Kualitas Udara
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
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </motion.div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-slate-600 dark:text-slate-400 text-sm"
              >
                OXYRA sedang memproses...
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-200 dark:border-slate-800 p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Tanyakan tentang kualitas udara..."
                className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <button
                onClick={handleSend}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center gap-2"
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
