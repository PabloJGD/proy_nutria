// src/app/page.tsx
'use client';

import { useSession, signIn, signOut } from 'next-auth/react';
import { useState, FormEvent, useRef, useEffect, ChangeEvent } from 'react';
import ReactMarkdown from 'react-markdown';

type Mensaje = { de: 'usuario' | 'bot'; texto: string; imagen?: string };

const SUGERENCIAS = [
  'Tengo pollo y arroz, ¿qué preparo?',
  'Quiero algo vegetariano y rápido',
  'Receta peruana baja en calorías',
  'Tengo 20 minutos para cocinar',
];

export default function Page() {
  const { data: session } = useSession();
  const [chat, setChat] = useState<Mensaje[]>([]);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [imagenFile, setImagenFile] = useState<File | null>(null);
  const [imagenPreview, setImagenPreview] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('nutria-theme');
    if (saved === 'dark') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat, loading]);

  const toggleDark = () => {
    const next = !darkMode;
    setDarkMode(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('nutria-theme', next ? 'dark' : 'light');
  };

  const handleImagenChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImagenFile(file);
    const reader = new FileReader();
    reader.onload = () => setImagenPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const limpiarImagen = () => {
    setImagenFile(null);
    setImagenPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const enviar = async (e: FormEvent) => {
    e.preventDefault();
    if (!msg.trim() && !imagenFile) return;
    const mensajeUsuario = msg.trim() || 'Analiza esta imagen de ingredientes.';
    setChat((c) => [...c, { de: 'usuario', texto: mensajeUsuario, imagen: imagenPreview ?? undefined }]);
    setMsg('');
    const archivoImagen = imagenFile;
    limpiarImagen();
    setLoading(true);
    try {
      const userEmail = session?.user?.email ?? '';
      let respuestaTexto = '';
      if (archivoImagen) {
        const formData = new FormData();
        formData.append('idagente', userEmail);
        formData.append('msg', mensajeUsuario);
        formData.append('image', archivoImagen);
        const res = await fetch('/api/agent', { method: 'POST', body: formData });
        respuestaTexto = await res.text();
      } else {
        const res = await fetch(`/api/agent?idagente=${encodeURIComponent(userEmail)}&msg=${encodeURIComponent(mensajeUsuario)}`);
        respuestaTexto = await res.text();
      }
      setChat((c) => [...c, { de: 'bot', texto: respuestaTexto }]);
    } catch {
      setChat((c) => [...c, { de: 'bot', texto: 'Hubo un error al conectar con el asistente. Por favor, intenta de nuevo.' }]);
    } finally {
      setLoading(false);
    }
  };

  // ── Login screen ─────────────────────────────────────────────────────────────
  if (!session) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-6 bg-gray-50 dark:bg-slate-900 px-4">
        <button
          onClick={toggleDark}
          className="absolute top-4 right-4 p-2 rounded-lg bg-gray-200 dark:bg-slate-700 text-gray-600 dark:text-gray-300 hover:opacity-80 transition-all"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
        <div className="text-center">
          <div className="text-6xl mb-4">🥗</div>
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 dark:text-white mb-2">Bienvenido a NutrIA</h2>
          <p className="text-gray-500 dark:text-gray-400 max-w-sm text-sm sm:text-base">
            Tu asistente personal de nutrición. Recibe recomendaciones de recetas personalizadas según tus ingredientes y objetivos de salud.
          </p>
        </div>
        <button
          onClick={() => signIn('google')}
          className="flex items-center gap-3 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-700 text-gray-700 dark:text-white font-semibold px-6 py-3 rounded-xl shadow-sm transition-all"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continuar con Google
        </button>
        <p className="text-gray-400 text-xs">Tus datos se usan solo para personalizar tu experiencia</p>
      </div>
    );
  }

  const userName = session.user?.name?.split(' ')[0] ?? session.user?.email;

  // ── App shell ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-dvh overflow-hidden">

      {/* Overlay mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-30
        w-64 bg-gradient-to-b from-green-800 to-green-900 dark:from-green-900 dark:to-slate-900
        text-white flex flex-col p-6 shadow-xl
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">🥗 NutrIA</h1>
            <p className="text-green-300 text-xs mt-1">Asistente de Nutrición con IA</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-green-300 hover:text-white text-xl leading-none"
          >
            ✕
          </button>
        </div>

        <div className="flex-1">
          <p className="text-green-400 text-xs uppercase font-semibold mb-3 tracking-wider">¿Qué puedo hacer?</p>
          <ul className="space-y-3 text-sm text-green-100">
            <li className="flex items-start gap-2"><span>🍽️</span><span>Recomendar recetas según tus ingredientes</span></li>
            <li className="flex items-start gap-2"><span>🇵🇪</span><span>Buscar platos de cocina peruana</span></li>
            <li className="flex items-start gap-2"><span>📊</span><span>Brindar información nutricional detallada</span></li>
            <li className="flex items-start gap-2"><span>📷</span><span>Analizar fotos de ingredientes</span></li>
            <li className="flex items-start gap-2"><span>🥗</span><span>Adaptar recetas a tus restricciones</span></li>
          </ul>
        </div>

        <div className="mt-auto">
          <p className="text-green-500 text-xs text-center">Powered by GPT-4o + LangGraph</p>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden bg-gray-50 dark:bg-slate-900 transition-colors duration-200">

        {/* Header */}
        <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 px-4 sm:px-6 py-3 flex justify-between items-center shadow-sm flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Hamburger — solo mobile */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <p className="font-semibold text-gray-800 dark:text-white text-sm sm:text-base">Hola, {userName} 👋</p>
              <p className="text-xs text-gray-400 hidden sm:block">{session.user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleDark}
              className="p-2 rounded-lg bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300 hover:opacity-80 transition-all"
              title={darkMode ? 'Modo claro' : 'Modo oscuro'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
            <button
              onClick={() => signOut()}
              className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 hover:text-red-500 border border-gray-200 dark:border-slate-600 hover:border-red-300 px-2 sm:px-3 py-1.5 rounded-lg transition-all"
            >
              Salir
            </button>
          </div>
        </header>

        {/* Chat */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4">
          {chat.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center gap-3 px-4">
              <div className="text-5xl">🍽️</div>
              <p className="font-medium text-gray-600 dark:text-gray-300">¿Qué tienes en la despensa hoy?</p>
              <p className="text-sm text-gray-400 dark:text-gray-500 max-w-xs">
                Cuéntame qué ingredientes tienes, sube una foto o dime qué tipo de comida deseas.
              </p>
              <div className="flex flex-wrap gap-2 mt-2 justify-center">
                {SUGERENCIAS.map((s) => (
                  <button
                    key={s}
                    onClick={() => setMsg(s)}
                    className="text-xs bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-700 px-3 py-1.5 rounded-full hover:bg-green-100 dark:hover:bg-green-900/50 transition-all"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {chat.map((m, i) => (
            <div key={i} className={`flex ${m.de === 'usuario' ? 'justify-end' : 'justify-start'}`}>
              {m.de === 'bot' && (
                <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-sm mr-2 flex-shrink-0 mt-1">
                  🥗
                </div>
              )}
              <div className={`max-w-[80%] sm:max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                m.de === 'usuario'
                  ? 'bg-green-600 text-white rounded-tr-sm'
                  : 'bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100 border border-gray-100 dark:border-slate-700 shadow-sm rounded-tl-sm'
              }`}>
                {m.imagen && (
                  <img src={m.imagen} alt="ingredientes" className="rounded-lg mb-2 max-h-40 w-full object-cover" />
                )}
                {m.de === 'bot' ? (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside my-1 space-y-0.5">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside my-1 space-y-0.5">{children}</ol>,
                      li: ({ children }) => <li className="ml-2">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      hr: () => <hr className="my-2 border-gray-300 dark:border-slate-600" />,
                    }}
                  >
                    {m.texto}
                  </ReactMarkdown>
                ) : (
                  m.texto
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-sm mr-2 flex-shrink-0">
                🥗
              </div>
              <div className="bg-white dark:bg-slate-800 border border-gray-100 dark:border-slate-700 shadow-sm px-4 py-3 rounded-2xl rounded-tl-sm">
                <div className="flex gap-1 items-center h-4">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 px-4 sm:px-6 py-3 sm:py-4 flex-shrink-0">
          {imagenPreview && (
            <div className="mb-3 flex items-center gap-3 bg-gray-50 dark:bg-slate-700 rounded-xl px-3 py-2">
              <img src={imagenPreview} alt="preview" className="h-12 w-12 rounded-lg object-cover flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-600 dark:text-gray-300 font-medium truncate">{imagenFile?.name}</p>
                <p className="text-xs text-gray-400">Lista para enviar</p>
              </div>
              <button onClick={limpiarImagen} className="text-gray-400 hover:text-red-500 transition-all text-xl leading-none flex-shrink-0">×</button>
            </div>
          )}

          <form onSubmit={enviar} className="flex gap-2 items-end">
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleImagenChange} />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2.5 sm:p-3 rounded-xl border border-gray-200 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 text-gray-500 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/30 hover:border-green-300 hover:text-green-600 transition-all flex-shrink-0"
              title="Subir imagen"
            >
              📎
            </button>

            <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleImagenChange} />
            <button
              type="button"
              onClick={() => cameraInputRef.current?.click()}
              className="p-2.5 sm:p-3 rounded-xl border border-gray-200 dark:border-slate-600 bg-gray-50 dark:bg-slate-700 text-gray-500 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/30 hover:border-green-300 hover:text-green-600 transition-all flex-shrink-0"
              title="Tomar foto"
            >
              📷
            </button>

            <textarea
              className="flex-1 resize-none rounded-xl border border-gray-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 px-3 sm:px-4 py-2.5 sm:py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent transition-all min-h-[44px] max-h-28"
              placeholder="Ej: Tengo tomate, cebolla y huevo..."
              value={msg}
              onChange={(e) => setMsg(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  enviar(e as unknown as FormEvent);
                }
              }}
              disabled={loading}
              rows={1}
            />

            <button
              type="submit"
              disabled={loading || (!msg.trim() && !imagenFile)}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-300 dark:disabled:bg-slate-600 text-white p-2.5 sm:p-3 rounded-xl font-medium text-sm transition-all flex-shrink-0"
            >
              {loading ? '...' : '➤'}
            </button>
          </form>

          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center hidden sm:block">
            Enter para enviar · Shift+Enter para nueva línea · 📎 subir imagen · 📷 tomar foto
          </p>
        </div>
      </div>
    </div>
  );
}
