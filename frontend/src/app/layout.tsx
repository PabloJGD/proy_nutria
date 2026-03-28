// src/app/layout.tsx
import './globals.css';
import type { ReactNode } from 'react';
import AuthProvider from './AuthProvider';

export const metadata = {
  title: 'NutrIA — Asistente de Nutrición con IA',
  description: 'Recomendaciones personalizadas de recetas y nutrición con inteligencia artificial.',
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="h-screen h-dvh bg-gray-50 dark:bg-slate-900 transition-colors duration-200 overflow-hidden">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
