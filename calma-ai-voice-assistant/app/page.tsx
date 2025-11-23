"use client"

import { useEffect } from "react"
import { BottomNav } from "@/components/bottom-nav"
import { initializeElevenLabsListener } from "@/lib/elevenlabs-integration"

export default function Page() {
  useEffect(() => {
    const script = document.createElement("script")
    script.src = "https://unpkg.com/@elevenlabs/convai-widget-embed"
    script.async = true
    script.setAttribute("data-lang", "es")
    
    // Inicializar listener cuando el script cargue
    script.onload = () => {
      console.log('📡 ElevenLabs widget loaded')
      initializeElevenLabsListener()
    }
    
    document.body.appendChild(script)
    
    return () => {
      // Cleanup
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [])

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent"></div>
          <span className="text-sm font-medium text-muted-foreground">Calma</span>
        </div>
        <button className="text-muted-foreground hover:text-foreground transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-between px-6 py-8 overflow-y-auto pb-20">
        {/* Welcome Section */}
        <div className="w-full max-w-md text-center space-y-6 pt-8">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-foreground">Calma</h1>
            <p className="text-muted-foreground text-sm">Tu compañero de bienestar mental</p>
          </div>
          
          <div className="space-y-4 text-left">
            <div className="bg-secondary/50 rounded-lg p-4 space-y-2">
              <h2 className="font-semibold text-foreground">¿Cómo puedo ayudarte?</h2>
              <p className="text-sm text-muted-foreground">
                Puedo ayudarte a encontrar especialistas en salud mental y proporcionarte información sobre:
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                <li>• Búsqueda de psicólogos y terapeutas</li>
                <li>• Manejo de ansiedad y estrés</li>
                <li>• Técnicas de relajación</li>
                <li>• Recursos de apoyo emocional</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Voice Assistant Widget - Positioned at bottom center */}
        <div className="w-full max-w-md flex flex-col items-center gap-4 pb-4">
          <p className="text-sm text-muted-foreground text-center">
            Presiona el botón para hablar conmigo
          </p>
          <div className="flex justify-center items-center w-full">
            <elevenlabs-convai agent-id="agent_6801kajzvktnemrtm1nxr93n92ed"></elevenlabs-convai>
          </div>
        </div>
      </main>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
