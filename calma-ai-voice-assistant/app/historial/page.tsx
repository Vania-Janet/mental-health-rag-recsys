"use client"

import { BottomNav } from "@/components/bottom-nav"

export default function HistorialPage() {
  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent"></div>
          <span className="text-sm font-medium text-muted-foreground">Calma - Historial</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-8 overflow-y-auto">
        <h1 className="text-2xl font-bold mb-6">Historial de Conversaciones</h1>
        
        <div className="text-center text-muted-foreground py-12">
          <svg 
            className="w-16 h-16 mx-auto mb-4 opacity-50" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-lg">Próximamente</p>
          <p className="text-sm mt-2">Aquí podrás ver el historial de tus conversaciones</p>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
